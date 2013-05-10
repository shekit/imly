from django.core.management.base import BaseCommand, CommandError
from imly.models import Store, Product
from plata.product.stock.models import StockTransaction,Period

class Command(BaseCommand):
    def handle(self, *args,**options):
    	print 'Reinitializing items in stock with capacity_per_day to be used by plata to restock...'
    	for product in Product.objects.all():
    		product.items_in_stock = product.capacity_per_day
    		product.save()
    	print 'Over to plata, to restock.'
    	print 'Plata, restocking...'
    	StockTransaction.objects.open_new_period()
    	print 'Plata, done restocking'