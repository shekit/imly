from django.dispatch import receiver
import decimal
from datetime import timedelta, datetime
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save, pre_delete
from django.core.mail import send_mail,EmailMessage,get_connection
from django.db.models import Sum
from plata.shop.models import Order
from plata.product.stock.models import Period, StockTransaction
from plata.shop.signals import contact_created
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
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import default_token_generator

@receiver(post_save,sender=Product)
def product_add_mail(sender,instance,created,**kwargs):
    if created:
        instance.app_label, instance.module_name = 'imly', 'product'
        msg = EmailMessage("New Product",get_template('email_templates/product_add_mail.html').render(Context({'product':instance})),settings.ADMIN_EMAIL,[settings.ADMIN_EMAIL])
        msg.content_subtype = "html"
        msg.send()


@receiver(contact_created)
def anonymous_checkout_created_account(sender, user, password, **kwargs):
    if password:
    	token_generator = kwargs.get("token_generator",default_token_generator)
    	temp_key = token_generator.make_token(user)
    	site = Site.objects.get(pk=settings.SITE_ID)
    	path = reverse("account_reset_password_from_key",kwargs=dict(uidb36=int_to_base36(user.id),key=temp_key))
    	url = 'http://%s%s' %(site.domain,path)
        msg = EmailMessage("Your imly.in password",get_template('email_templates/anonymous_checkout_created_account.html').render(Context({'user':user,'password':password,'password_reset_url':url})),settings.ADMIN_EMAIL,[user.email],bcc=[settings.ADMIN_EMAIL])
        msg.content_subtype = "html"
        msg.send()

@receiver(post_save,sender=ReviewedItem)
def reviewed_mail(sender,instance,created,**kwargs):
	if created:
		site = Site.objects.get(pk=settings.SITE_ID)
		msg = EmailMessage("Reviews",get_template('email_templates/reviews_mail_admin.html').render(Context({'review':instance, 'site': site})),settings.ADMIN_EMAIL,[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()
		msg = EmailMessage("You just got a review!",get_template('email_templates/reviews_mail_store.html').render(Context({'review':instance, 'site': site})),settings.SIGNUP_EMAIL,[instance.content_object.store.owner.email])
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
                site = Site.objects.get(pk=settings.SITE_ID)
                product1 = Product.objects.is_approved().filter(is_bestseller=True, is_flag=False)[0]
                product2 = Product.objects.is_approved().filter(is_bestseller=True, is_flag=False)[1]
                product3 = Product.objects.is_approved().filter(is_bestseller=True, is_flag=False)[2]
                product4 = Product.objects.is_approved().filter(is_bestseller=True, is_flag=False)[3]
                product5 = Product.objects.is_approved().filter(is_deleted=False, is_flag=False).order_by("-date_created")[0]
                product6 = Product.objects.is_approved().filter(is_deleted=False, is_flag=False).order_by("-date_created")[1]
		msg = EmailMessage("Welcome to Imly!",get_template('email_templates/user_sign_up_email.html').render(Context({'user':instance, 'product1':product1,'product2':product2,'product3':product3,'product4':product4,'product5':product5,'product6':product6, 'site':site})),settings.SIGNUP_EMAIL,[instance.email])
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
def imly_fly_by_night(sender,instance,**kwargs):
	if instance.status == Order.IMLY_CONFIRMED and not instance.data.get('imly_fly_by_knight',''):
		storeorder = instance.storeorder_set.filter(pick_up = False,delivery_charges__gt=0)
		if storeorder:
			msg = EmailMessage("New Imly.in Order",get_template('email_templates/fly_by_knight.html').render(Context({'storeorders':storeorder,'order':instance})),settings.ORDERS_EMAIL,['neha@flybyknight.in'],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()
			post_save.disconnect(imly_fly_by_night,sender=Order)
			instance.data['imly_fly_by_knight'] = 'send'
			instance.save()
			post_save.connect(imly_fly_by_night,sender=Order)
    
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
			msg=EmailMessage("You got a new order - %s" %(instance._order_id),get_template('email_templates/imly_order_confirmed.html').render(Context({'store':store,'storeorder':storeorder,'product_detail':product_detail,'buyer_info':instance})),settings.ORDERS_EMAIL,[store.owner.email],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()
		msg = EmailMessage("Your Imly order - %s." % (instance._order_id),get_template('email_templates/imly_order_confirmed_buyer.html').render(Context({'order':instance})),settings.ORDERS_EMAIL,[instance.email],bcc=[settings.ADMIN_EMAIL])
		msg.content_subtype = "html"
		msg.send()
		post_save.disconnect(imly_confirmed_send_mail_store_owner,sender=Order)
		instance.data['imly_confirmed'] = 'confirmed'
		instance.save()
		post_save.connect(imly_confirmed_send_mail_store_owner,sender=Order)

@receiver(post_save,sender=Order)
def set_store_order(sender,instance,**kwargs):	
    StoreOrder.update_for_order(instance)
    
@receiver(m2m_changed, sender=Product.tags.through)
def update_store_tags_from_product(sender, instance, action, **kwargs):
    if action == 'post_add':
        instance.store.reset_tags()

@receiver(post_save, sender=Product)
def update_store_categories_from_product(sender, instance, **kwargs):
    instance.store.reset_categories()

@receiver(pre_delete, sender=Product)
def update_store_tags_and_categories_from_product(sender, instance, **kwargs):
    instance.store.reset_tags()
    instance.store.reset_categories()        
        
@receiver(post_save, sender=Store)
def update_product_geography(sender, instance, **kwargs):
    post_save.disconnect(sender=Product)
    for product in instance.product_set.all():
        product.pick_up_point = instance.pick_up_point
        product.save()
    post_save.connect(update_store_categories_from_product, sender=Product)
    
@receiver(post_save, sender=Store)
def send_store_mail(sender,instance,created, **kwargs):
    if created:# and Site.objects.get_current().domain == 'imly.in':
    	msg=EmailMessage("Store added.",get_template('email_templates/imly_store_created_admin.html').render(Context({'store':instance})),instance.owner.email,[settings.STORE_EMAIL])
    	msg.content_subtype = "html"
    	msg.send()
    	msg=EmailMessage("Your shop will be reviewed soon!",get_template('email_templates/imly_store_created_owner.html').render(Context({'store':instance})),settings.STORE_EMAIL,[instance.owner.email],bcc=[settings.ADMIN_EMAIL])
    	msg.content_subtype = "html"
    	msg.send()

@receiver(post_save,sender=Store)
def store_approved_email(sender,instance,created,**kwargs):
	if instance.is_approved and not instance.data.get('email',''):# and Site.objects.get_current().domain == 'imly.in':
		msg=EmailMessage("Your shop's been approved!",get_template('email_templates/imly_store_confirmed.html').render(Context({'store':instance})),settings.STORE_EMAIL,[instance.owner.email],bcc=[settings.ADMIN_EMAIL])
		msg.content_subtype = 'html'
		msg.send()
		post_save.disconnect(store_approved_email,sender=Store)
		instance.data['email'] = 'sent'
		instance.save()
		post_save.connect(store_approved_email,sender=Store)