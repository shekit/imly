from django.contrib.gis.db import models

class StoreManager(models.GeoManager):
    
    def is_approved(self):
        return self.filter(is_approved=True)

    def is_featured(self):
        return self.is_approved().filter(is_featured=True)
    

class ProductManager(models.GeoManager):

    def is_approved(self):
        from imly.models import Store
        return self.filter(store__in=Store.objects.is_approved().all())

    def is_flag(self):
        return self.filter(is_flag = False)
        
class SpecialManager(models.Manager):
    
    def has_active_and_live(self):
        return self.filter(live=True, active=True).count()
            
    def current(self):
        return self.has_active_and_live() and self.filter(live=True, active=True).order_by('priority')[0]
