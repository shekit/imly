from django.dispatch import receiver
import decimal
from datetime import timedelta
from django.db.models import Max
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save
from django.core.mail import send_mail,EmailMessage,get_connection
from django.db.models import Sum
from plata.shop.models import Order
from plata.product.stock.models import Period, StockTransaction
from imly.models import Product, Store,DeliveryLocation,StoreOrder
from django.contrib.sites.models import Site
from django.contrib.gis.geos import Point, MultiPoint
from django.contrib.auth.models import User
from imly.utils import geocode
from django.template.loader import get_template
from django.template import Context

#@receiver(post_save,sender=User)
def sign_up_email(sender,instance,created,**kwargs):
	if created:
		msg = EmailMessage("Welcome to Imly.",get_template('email_templates/user_sign_up_email.html').render(Context({'user':instance})),'Imly <hello@imly.in>',[instance.email])
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

#@receiver(post_save,sender=Order)
def imly_order_place_send_email_admin(sender,instance,**kwargs):
	if instance.status == Order.PAID and not instance.data.get('paid',''):
		msg = EmailMessage("New Order %s Placed." % (instance._order_id),get_template('email_templates/imly_admin_order_email.html').render(Context({'order':instance})),'Imly Orders <orders@imly.in>',['imlyfood@gmail.com'])
		msg.content_subtype = "html"
		msg.send()
		post_save.disconnect(imly_order_place_send_email_admin,sender=Order)
		instance.data['paid'] = 'PAID'
		instance.save()
		post_save.connect(imly_order_place_send_email_admin,sender=Order)
    
#@receiver(post_save,sender=Order)
def imly_confirmed_send_mail_store_owner(sender,instance,**kwargs):
	if instance.status == Order.IMLY_CONFIRMED and not instance.data.get('imly_confirmed',''):
		stores = [stores for stores in instance.store_set.all()]
		for store in stores:
			print "Store Name", store
			for storeorder in store.storeorder_set.filter(order=instance):
				product_detail = []
				for detail in storeorder.order.items.all():
					if detail.product.store == store:
						product_detail.append(detail)
			msg=EmailMessage("New Order - %s" %(instance._order_id),get_template('email_templates/imly_order_confirmed.html').render(Context({'store':store,'storeorder':storeorder,'product_detail':product_detail,'buyer_info':instance})),"Imly Orders <orders@imly.in>",[store.owner.email])
			msg.content_subtype = "html"
			msg.send()
		msg = EmailMessage("Order %s." % (instance._order_id),get_template('email_templates/imly_order_confirmed_buyer.html').render(Context({'order':instance})),'Imly Orders <orders@imly.in>',[instance.email])
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

#@receiver(pre_save,sender=Order)
def set_store_info(sender,instance,**kwargs):
	stores = set((item.product.store for item in instance.items.all()))
	instance.data['store_info'] = []
	for store in stores:
		instance.data['store_info'].append((
			store.id,
			store.name,
			store.slug,
			sum((item.subtotal for item in instance.items.filter(product__in=store.product_set.all()))),
			instance.created.date() + timedelta(days=instance.items.filter(product__in=store.product_set.all()).aggregate(max=Max('product__lead_time'))['max'])
			))
		print instance.data

#@receiver(post_save, sender=Product)
def set_product_initial_transaction(sender,instance, created,**kwargs):
	period = Period.objects.current()
	if created:
		post_save.disconnect(set_product_initial_transaction,sender=Product)
		instance.initial_cpm = instance.capacity_per_month
		instance.save()
		post_save.connect(set_product_initial_transaction,sender=Product)
		print 'post_save for initial', instance.initial_cpm
		instance.stock_transactions.create(period=period,type=StockTransaction.INITIAL,change=instance.capacity_per_month)
	else:
#		print instance.capacity_per_month , StockTransaction.objects.items_in_stock(instance)
#		if instance.capacity_per_month > StockTransaction.objects.items_in_stock(instance) :
		sale_transaction = instance.stock_transactions.filter(type=StockTransaction.SALE).aggregate(sale_sum = Sum('change'))
		sale_sum = sale_transaction['sale_sum']
		#locals().update(sale_transaction)#convert the from dictionary to varible
		if instance.initial_cpm != instance.capacity_per_month:
			if instance.capacity_per_month > instance.initial_cpm:
				if instance.initial_cpm <= abs(sale_sum):
					instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change=instance.capacity_per_month - abs(sale_sum))					
					instance.stock_transactions.items_in_stock(instance,update=True)	
					post_save.disconnect(set_product_initial_transaction,sender=Product)
					instance.initial_cpm = instance.capacity_per_month
					instance.save()
					post_save.connect(set_product_initial_transaction,sender=Product)
				instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change=instance.capacity_per_month - instance.initial_cpm)
				instance.stock_transactions.items_in_stock(instance,update=True)
				post_save.disconnect(set_product_initial_transaction,sender=Product)
				instance.initial_cpm = instance.capacity_per_month
				instance.save()
				post_save.connect(set_product_initial_transaction,sender=Product)	
			else:
				if instance.capacity_per_month > abs(sale_sum):#convert the positive value
					instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change=instance.capacity_per_month - instance.initial_cpm)
					instance.stock_transactions.items_in_stock(instance,update=True)
					post_save.disconnect(set_product_initial_transaction,sender=Product)
					instance.initial_cpm = instance.capacity_per_month
					instance.save()
					post_save.connect(set_product_initial_transaction,sender=Product)
				else:
					print "Capacity per month is not less than sale_transaction"
					instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change= - (instance.stock_transactions.items_in_stock(instance,update=True)))
					instance.stock_transactions.items_in_stock(instance,update=True)
					post_save.disconnect(set_product_initial_transaction,sender=Product)
					instance.initial_cpm = instance.capacity_per_month
					instance.save()
					post_save.connect(set_product_initial_transaction,sender=Product)
		else:
			print "Same"


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
        
#@receiver(post_save, sender=Store)
def update_product_geography(sender, instance, **kwargs):
    post_save.disconnect(sender=Product)
    for product in instance.product_set.all():
        product.pick_up_point = instance.pick_up_point
        product.delivery_points = instance.delivery_points
        product.save()
    post_save.connect(update_store_categories_from_product, sender=Product)
    

#@receiver(post_save, sender=Store)
def send_store_mail(sender,instance,created, **kwargs):
    if created:# and Site.objects.get_current().domain == 'imly.in':
    	msg=EmailMessage("Store added.",get_template('email_templates/imly_store_created_admin.html').render(Context({'store':instance})),instance.owner.email,['imlyfood@gmail.com'])
    	msg.content_subtype = "html"
    	msg.send()
    	msg=EmailMessage("Store added.",get_template('email_templates/imly_store_created_owner.html').render(Context({'store':instance})),'Imly <hello@imly.in>',[instance.owner.email])
    	msg.content_subtype = "html"
    	msg.send()


#@receiver(post_save,sender=Store)
def store_approved_email(sender,instance,created,**kwargs):
	if instance.is_approved and not instance.data.get('email',''):# and Site.objects.get_current().domain == 'imly.in':
		msg=EmailMessage("Store Approved.",get_template('email_templates/imly_store_confirmed.html').render(Context({'store':instance})),'Imly <hello@imly.in>',[instance.owner.email])
		msg.content_subtype = 'html'
		msg.send()
		post_save.disconnect(store_approved_email,sender=Store)
		instance.data['email'] = 'sent'
		instance.save()
		post_save.connect(store_approved_email,sender=Store)