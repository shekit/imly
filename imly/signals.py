from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from plata.product.stock.models import Period, StockTransaction
from imly.models import Product, Store, Category

@receiver(post_save, sender=Product)
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

		'''if instance.capacity_per_month != initial_transaction.change:
			if not instance.stock_transactions.filter(type=StockTransaction.CORRECTION):

			sale_transaction = instance.stock_transactions.filter(type=StockTransaction.SALE).aggregate(Sum('change'))
		print 'Capacity per month', instance.capacity_per_month
		print 'Item in staock', instance.items_in_stock
		print 'StockTransaction.objects.items_in_stock(instance)',StockTransaction.objects.items_in_stock(instance)
		instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change=(instance.capacity_per_month - StockTransaction.objects.items_in_stock(instance)) + sale_transaction['change__sum'])'''
		'''if instance.capacity_per_month != initial_transaction.change:
			initial_transaction = instance.stock_transactions.filter(type=StockTransaction.INITIAL)[0]
			sale_transaction = instance.stock_transactions.filter(type=StockTransaction.SALE).aggregate(Sum('change'))
			if instance.capacity_per_month > initial_transaction.change:

				print 'Item in Stock :',(initial_transaction.change + (instance.capacity_per_month - initial_transaction.change)) + sale_transaction['change__sum']
				print 'capacity_per_month:',initial_transaction.change + (instance.capacity_per_month - initial_transaction.change)
			period = Period.objects.current()
		print 'After Update:',instance.capacity_per_month, instance.items_in_stock
		instance.stock_transactions.create(period=period,type=StockTransaction.CORRECTION,change=instance.capacity_per_month - instance.items_in_stock)'''

		

@receiver(post_save, sender="Product")
def add_category(sender, **kwargs):
    sender.store.categories.add(sender.category)
        
@receiver(post_delete, sender="Product")
def delete_category(sender, **kwargs):
    if sender.store.product_set.filter(category=sender.category):
        return
    else:
        sender.store.categories.remove(sender.category)