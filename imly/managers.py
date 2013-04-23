from django.db import models

class StoreManager(models.Manager):
    
    def is_approved(self):
        return self.filter(is_approved=True)

    def is_featured(self):
        return self.is_approved().filter(is_featured=True)
    

class ProductManager(models.Manager):

    def is_approved(self):
        from imly.models import Store
        return self.filter(store__in=Store.objects.is_approved().all())