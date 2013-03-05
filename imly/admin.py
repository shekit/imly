from django.contrib import admin

from imly.models import *

from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order


class CategoryAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}

class LocationAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}

class StoreAdmin(admin.ModelAdmin):
    
    list_display = ["name","owner", "is_approved", "is_featured"]
    list_filter = ["is_approved", "is_featured"]
    prepopulated_fields = {"slug":("name",)}

class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["name","store", "category","get_price", "capacity_per_month", "lead_time", "is_featured", "is_bestseller"]
    list_filter = ["store", "is_featured"]
    prepopulated_fields = {"slug":("name",)}
    
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)

#Plata Models - already registered

#admin.site.register(Contact)
#admin.site.register(Discount)
#admin.site.register(Order)