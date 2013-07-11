from django.core.management.base import BaseCommand, CommandError
from imly.models import Product,Store
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
from datetime import date,timedelta

class Command(BaseCommand):
	def handle(self,*args,**options):
		for store in Store.objects.filter(product__is_flag=True,product__date_created__startswith=date.today()):
			msg = EmailMessage("Flagged Products",get_template('email_templates/flag_products_mail.html').render(Context({'store':store})),settings.ADMIN_EMAIL,[store.owner.email],bcc=[settings.ADMIN_EMAIL])
			msg.content_subtype = "html"
			msg.send()