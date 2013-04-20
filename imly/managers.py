from django.db import models

class StoreManager(models.Manager):
    
    def get_query_set(self):
    	return super(StoreManager, self).get_query_set().filter(is_approved=True)

    def is_featured(self):
        return self.approved_stores().filter(is_featured=True)
    

class ProductManager(models.Manager):
    
    def get_query_set(self):
    	from models import Store
    	return super(ProductManager, self).get_query_set().filter(is_deleted = False, store__in=Store.objects.all())
