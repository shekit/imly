from django.dispatch import receiver
import decimal
from datetime import timedelta
from django.db.models import Max
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save
from django.core.mail import send_mail,EmailMessage,get_connection
from django.db.models import Sum
from plata.shop.models import Order
from plata.product.stock.models import Period, StockTransaction
from imly.models import Product, Store,DeliveryLocation,StoreOrder,ChefTip
from django.contrib.sites.models import Site
from django.contrib.gis.geos import Point, MultiPoint
from django.contrib.auth.models import User
from imly.utils import geocode
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from reviews.models import ReviewedItem
from imly.utils import geocode, tracker

@receiver(post_save,sender=ReviewedItem)
def reviewed_mail(sender,instance,created,**kwargs):
	if created:
		site = Site.objects.get(pk=settings.SITE_ID)
		msg = EmailMessage("Reviews",get_template('email_templates/reviews_mail_admin.html').render(Context({'review':instance, 'site': site})),settings.ADMIN_EMAIL,[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()
		msg = EmailMessage("Reviews",get_template('email_templates/reviews_mail_store.html').render(Context({'review':instance, 'site': site})),settings.SIGNUP_EMAIL,[instance.content_object.store.owner.email])
		msg.content_subtype = "html"
		msg.send()
		
@receiver(post_save,sender=ChefTip)
def cheftip_mail(sender,instance,created,**kwargs):
	if created:
		msg = EmailMessage("Chef tip by %s" %(instance.your_name),get_template('email_templates/cheftip_mail.html').render(Context({"chef":instance})),settings.ADMIN_EMAIL,[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()

@receiver(post_save,sender=User)
def sign_up_email(sender,instance,created,**kwargs):
	if created:
		msg = EmailMessage("Welcome to Imly.",get_template('email_templates/user_sign_up_email.html').render(Context({'user':instance})),settings.SIGNUP_EMAIL,[instance.email])
		msg.content_subtype = "html"
		msg.send()

@receiver(post_save,sender=User)
def sign_up_email_admin(sender,instance,created,**kwargs):
	if created:
		msg = EmailMessage("New user",'%s has sign up through imly.in' %(instance.first_name),settings.SIGNUP_EMAIL,[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()

@receiver(pre_save, sender=User)
def save_first_name(sender, instance, **kwargs):
    first_name = instance.email.split("@")[0]
    instance.first_name = first_name

@receiver(pre_save,sender=DeliveryLocation)
def set_location_point(sender,instance,**kwargs):
    result = geocode(instance.name)
    if result:
        point = Point(*result[1])
        instance.location = point

@receiver(post_save,sender=Order)
def imly_order_place_send_email_admin(sender,instance,**kwargs):
	if instance.status == Order.PAID and not instance.data.get('paid',''):
		msg = EmailMessage("New Order %s Placed." % (instance._order_id),get_template('email_templates/imly_admin_order_email.html').render(Context({'order':instance})),settings.ORDERS_EMAIL,[settings.ORDERS_EMAIL])
		msg.content_subtype = "html"
		msg.send()
		post_save.disconnect(imly_order_place_send_email_admin,sender=Order)
		instance.data['paid'] = 'PAID'
		instance.save()
		post_save.connect(imly_order_place_send_email_admin,sender=Order)
    
@receiver(post_save,sender=Order)
def imly_confirmed_send_mail_store_owner(sender,instance,**kwargs):
	if instance.status == Order.IMLY_CONFIRMED and not instance.data.get('imly_confirmed',''):
		stores = [stores for stores in instance.store_set.all()]
		for store in stores:
			for storeorder in store.storeorder_set.filter(order=instance):
				product_detail = []
				for detail in storeorder.order.items.all():
					if detail.product.store == store:
						product_detail.append(detail)
			msg=EmailMessage("New Order - %s" %(instance._order_id),get_template('email_templates/imly_order_confirmed.html').render(Context({'store':store,'storeorder':storeorder,'product_detail':product_detail,'buyer_info':instance})),settings.ORDERS_EMAIL,[store.owner.email],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()
		msg = EmailMessage("Order %s." % (instance._order_id),get_template('email_templates/imly_order_confirmed_buyer.html').render(Context({'order':instance})),settings.ORDERS_EMAIL,[instance.email],bcc=[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()
		post_save.disconnect(imly_confirmed_send_mail_store_owner,sender=Order)
		instance.data['imly_confirmed'] = 'confirmed'
		instance.save()
		post_save.connect(imly_confirmed_send_mail_store_owner,sender=Order)

@receiver(post_save,sender=Order)
def set_store_order(sender,instance,**kwargs):	
    stores = set((item.product.store for item in instance.items.all()))
    StoreOrder.objects.filter(order=instance).exclude(store__in=stores).delete()
    for store in stores:
        store_order, created = StoreOrder.objects.get_or_create(store=store,order=instance)
        store_order.delivered_by_product_lead = instance.created + timedelta(days=instance.items.filter(product__in=store.product_set.all()).aggregate(max = Max('product__lead_time'))['max'])
        store_order.store_total = sum((item.subtotal for item in instance.items.filter(product__in=store.product_set.all())))
        store_order.store_items = instance.items.filter(product__in=store.product_set.all()).count()
        store_order.save()

@receiver(m2m_changed, sender=Product.tags.through)
def update_store_tags_from_product(sender, instance, action, **kwargs):
    if action == 'post_add':
        instance.store.reset_tags()

@receiver(post_save, sender=Product)
def update_store_categories_from_product(sender, instance, **kwargs):
    instance.store.reset_categories()

@receiver(post_delete, sender=Product)
def update_store_tags_and_categories_from_product(sender, instance, **kwargs):
    instance.store.reset_tags()
    instance.store.reset_categories()        
        
@receiver(post_save, sender=Store)
def update_product_geography(sender, instance, **kwargs):
    post_save.disconnect(sender=Product)
    for product in instance.product_set.all():
        product.pick_up_point = instance.pick_up_point
        product.delivery_points = instance.delivery_points
        product.save()
    post_save.connect(update_store_categories_from_product, sender=Product)
    
@receiver(post_save, sender=Store)
def send_store_mail(sender,instance,created, **kwargs):
    if created:# and Site.objects.get_current().domain == 'imly.in':
    	msg=EmailMessage("Store added.",get_template('email_templates/imly_store_created_admin.html').render(Context({'store':instance})),instance.owner.email,[settings.STORE_EMAIL])
    	msg.content_subtype = "html"
    	msg.send()
    	msg=EmailMessage("Store added.",get_template('email_templates/imly_store_created_owner.html').render(Context({'store':instance})),settings.STORE_EMAIL,[instance.owner.email],bcc=[settings.ADMIN_EMAIL])
    	msg.content_subtype = "html"
    	msg.send()

@receiver(post_save,sender=Store)
def store_approved_email(sender,instance,created,**kwargs):
	if instance.is_approved and not instance.data.get('email',''):# and Site.objects.get_current().domain == 'imly.in':
		msg=EmailMessage("Store Approved.",get_template('email_templates/imly_store_confirmed.html').render(Context({'store':instance})),settings.STORE_EMAIL,[instance.owner.email],bcc=[settings.ADMIN_EMAIL])
		msg.content_subtype = 'html'
		msg.send()
		post_save.disconnect(store_approved_email,sender=Store)
		instance.data['email'] = 'sent'
		instance.save()
		post_save.connect(store_approved_email,sender=Store)