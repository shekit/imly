from dajngo.core.management.base import BaseCommand, CommandError
from imly.models import StoreOrder
from plata.shop.models import Order
from django.template.loader import get_template
from django.conf import settings
from django.template import Context
from django.core.mail import EmailMessage
from datetime import date,timedelta
from django.contrib.sites.models import Site

class Command(BaseCommand):
	def handle(self,*args,**options):
		site = Site.objects.get(pk = settings.SITE_ID)
		for sto in StoreOrder.objects.filter(order__status = Order.IMLY_CONFIRMED, delivered_on__startswith=date.today() - timedelta(days=1)):
			msg = EmailMessage("Did you like %s's food?" % (sto.store.name),get_template('email_templates/review_product_after_delivery.html').render(Context({'storeorder':sto,'site':site})),settings.SIGNUP_EMAIL,[sto.order.email])
			msg.content_subtype = "html"
			msg.send()