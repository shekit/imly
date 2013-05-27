from django.dispatch import receiver
import decimal
from datetime import timedelta
from django.db.models import Max
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save
from django.core.mail import send_mail
from django.db.models import Sum
from plata.shop.models import Order
from plata.product.stock.models import Period, StockTransaction
from imly.models import Product, Store,DeliveryLocation,StoreOrder
from django.contrib.sites.models import Site
from django.contrib.gis.geos import Point, MultiPoint
from omgeo.places import PlaceQuery
from omgeo.services import Bing
from django.contrib.auth.models import User
        
bingeo = Bing(settings={'api_key': 'AgOr3aEARXNVLGGSQe9nt2j6v9ThHyIiSNyWmoO5uw2N5RSfjt3MLBsxB_kgJTFn'})

@receiver(pre_save, sender=User)
def save_first_name(sender, instance, **kwargs):
    first_name = instance.email.split("@")[0]
    instance.first_name = first_name

@receiver(pre_save,sender=DeliveryLocation)
def set_location_point(sender,instance,**kwargs):
    pq = PlaceQuery(instance.name)
    result = bingeo.geocode(pq)
    geo = result[0][0]
    point = Point(geo.x, geo.y)
    instance.location = point
    
@receiver(post_save,sender=Order)
def imly_confirmed_send_mail(sender,instance,**kwargs):
	if instance.status == Order.IMLY_CONFIRMED:
		stores = [stores for stores in instance.store_set.all()]
		for store in stores:
			print "Store Name", store
			for storeorder in store.storeorder_set.filter(order=instance):
				product_detail = []
				for detail in storeorder.order.items.all():
					if detail.product.store == store:
						product_detail.append((detail,detail.quantity))
						#send_mail("Order Confirmed.","Your order is confirmed by Imly and you order id is %s" %(storeorder.order.order_id),"orders@imly.in",store.owner.email,fail_silently=False)
			print "Store Order detail",store,storeorder.order.order_id,product_detail,storeorder.delivered_on.date(),storeorder.store_total,instance.user.username
		buyer_email = instance.user.email
		print "Buyer Email",buyer_email
		#send_mail("Order Confirmed.","Your order is confirmed by Imly and you order id is %s" %(instance_id),"orders@imly.in",buyer_email,fail_silently=False)

@receiver(post_save,sender=Order)
def set_store_order(sender,instance,**kwargs):	
    stores = set((item.product.store for item in instance.items.all()))
    StoreOrder.objects.filter(order=instance).exclude(store__in=stores).delete()
    for store in stores:
        store_order, created = StoreOrder.objects.get_or_create(store=store,order=instance)
        store_order.delivered_on = instance.created + timedelta(days=instance.items.filter(product__in=store.product_set.all()).aggregate(max = Max('product__lead_time'))['max'])
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
    if created and Site.objects.get_current().domain == 'imly.in':
        send_mail("Store added - Awaiting Confirmation @%s" % (Site.objects.get_current(), ),"Store has been added by %s" % (instance.owner), instance.owner.email , ["imlyfood@gmail.com"], fail_silently=False)
