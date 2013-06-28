from django.contrib import admin
from django.contrib.gis import admin as gadmin
from imly.models import Category, Tag, Location, Product, Store, ChefTip, UserProfile, StoreOrder,DeliveryLocation, City, Special
from imagekit.admin import AdminThumbnail
from rollyourown.seo.admin import register_seo_admin
from seo import ImlyMetadata

register_seo_admin(admin.site, ImlyMetadata)

class CategoryAdmin(admin.ModelAdmin):
    
    list_display = ["name", "super_category", "is_active", 'product_ordering']
    prepopulated_fields = {"slug":("name",)}
    list_filter = ["super_category"]
    
    
class TagAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}


class LocationAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}

class DeliveryLocationInline(admin.TabularInline):
    model = DeliveryLocation
    fields=("name",)


class StoreAdmin(admin.ModelAdmin):
    
    list_display = ["name","owner", 'pick_up_location', 'delivers_to','no_of_product', "is_approved", "is_featured"]
    list_filter = ["is_approved", "is_featured"]
    inlines = [DeliveryLocationInline,]

    def no_of_product(self,instance):
        return instance.product_set.count()

    def queryset(self,request):
        qs = self.model.everything.all()
        ordering = self.ordering or ()
        if ordering:
            qs=qs.order_by(*ordering)
        return qs

class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["admin_thumbnail","name","store", "category", '_unit_price', "lead_time", "capacity_per_day", "is_bestseller","is_flag"]
    list_filter = [ "is_featured", 'category', "store","is_flag"]
    admin_thumbnail = AdminThumbnail(image_field="image_thumbnail_mini")
    list_display_links = ("name",)
    
    def queryset(self,request):
        qs = self.model.everything.all()
        ordering = self.ordering or ()
        if ordering:
            qs=qs.order_by(*ordering)
        return qs
    
class ChefTipAdmin(admin.ModelAdmin):
    
    list_display = ["name", "tip_contact_number", "your_name","create"]
    
class UserProfileAdmin(admin.ModelAdmin):
    
    list_display = ["user","first_name","last_name"]


class StoreOrderAdmin(admin.ModelAdmin):

    list_display = ["order","store","delivered_on","store_total","store_items"]

class SpecialAdmin(admin.ModelAdmin):
    list_display = ["title","slug","active","live","priority","created"]

class CityGeoAdmin(gadmin.OSMGeoAdmin):
    default_lon=98.962880
    default_lat=20.5936840
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ChefTip, ChefTipAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StoreOrder,StoreOrderAdmin)
gadmin.site.register(City, CityGeoAdmin)
admin.site.register(Special,SpecialAdmin)