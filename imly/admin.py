from django.contrib import admin

from imly.models import Category, Tag, Location, Product, Store

from imagekit.admin import AdminThumbnail



class CategoryAdmin(admin.ModelAdmin):
    
    list_display = ["name", "super_category", "is_active"]
    prepopulated_fields = {"slug":("name",)}
    list_filter = ["super_category"]
    
    
class TagAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}


class LocationAdmin(admin.ModelAdmin):
    
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug":("name",)}

class StoreAdmin(admin.ModelAdmin):
    
    list_display = ["name","owner", "is_approved", "is_featured"]
    list_filter = ["is_approved", "is_featured"]
    prepopulated_fields = {"slug":("name",)}

    def queryset(self,request):
        qs = self.model.everything.all()
        ordering = self.ordering or ()
        if ordering:
            qs=qs.order_by(*ordering)
        return qs

class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["admin_thumbnail","name","store", "category", "capacity_per_day", "lead_time", "is_featured", "is_bestseller"]
    list_filter = ["store", "is_featured"]
    prepopulated_fields = {"slug":("name",)}
    admin_thumbnail = AdminThumbnail(image_field="image_thumbnail_mini")
    list_display_links = ("name",)
    
    def queryset(self,request):
        qs = self.model.everything.all()
        ordering = self.ordering or ()
        if ordering:
            qs=qs.order_by(*ordering)
        return qs
 
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)