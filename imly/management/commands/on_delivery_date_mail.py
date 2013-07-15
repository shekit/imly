from django.core.management.base import BaseCommand, CommandError
from imly.models import StoreOrder
from plata.shop.models import Order
from django.template.loader import get_template
from django.conf import settings
from django.template import Context
from django.core.mail import EmailMessage
from datetime import date,timedelta

class Command(BaseCommand):
	def handle(self,*args,**options):
		for storeorder in StoreOrder.objects.filter(order__status = Order.IMLY_CONFIRMED,delivered_on__startswith = date.today()):
			product_detail = []
			for orderitem in storeorder.order.items.all():
				if orderitem.product.store == storeorder.store:
					product_detail.append(orderitem)
			msg = EmailMessage("Reminder: Order due today",get_template('email_templates/reminder_delivery_store.html').render(Context({'store':storeorder.store,'product_detail':product_detail,'storeorder':storeorder})),settings.ORDERS_EMAIL,[storeorder.store.owner.email],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()
			msg = EmailMessage("Reminder: Order due today",get_template('email_templates/reminder_delivery_buyer.html').render(Context({'order':storeorder.order,'store':storeorder.store,'store_total':storeorder.store_total})),settings.ORDERS_EMAIL,[storeorder.order.email],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()