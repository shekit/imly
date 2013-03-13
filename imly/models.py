from django.db import models
from django.contrib.auth.models import User

from plata.product.models import ProductBase
from plata.shop.models import PriceBase, Order

from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.views import Shop

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from markdown import markdown

from imly_project.settings import MEDIA_ROOT

from imly.managers import StoreManager, ProductManager

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.



class Category(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=False)
    super_category = models.ForeignKey("self", blank=True, null=True, related_name="sub_categories")
    position = models.IntegerField(default=1)
    
    tags = models.ManyToManyField("Tag", blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["position","name"]
    
    def __unicode__(self):
        return self.name

#how to create filter for multiple tags
#if has count , make it active?
class Tag(models.Model):
    
    name= models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["name"]
        
    def __unicode__(self):
        return self.name

class Location(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name
    


class Store(models.Model):
    #Store Details
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.OneToOneField(User)
    description = models.TextField()
    description_html = models.TextField(editable=False, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    
    #metadata
    categories = models.ManyToManyField(Category, blank=True)
    delivery_areas = models.ManyToManyField(Location)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True)
    
    #status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    tags = models.ManyToManyField(Tag)
    
    objects = StoreManager() #default manager
    
    
    class Meta:
        ordering = ["-date_created"]
    
    def __unicode__(self):
        return "%s by %s" % (self.name, self.owner)
    
    @models.permalink
    def get_absolute_url(self):
        return ("imly_store_detail", (), {"slug": self.slug})
    
    def save(self,*args, **kwargs):
        self.description_html = markdown(self.description)
        super(Store, self).save(*args, **kwargs)
        

class Product(ProductBase, PriceBase):
    #Product Details
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    capacity_per_month = models.IntegerField()
    description = models.TextField(blank=True)
    description_html = models.TextField(editable=False, blank=True)
    
    lead_time = models.IntegerField(default=1)
    category = models.ForeignKey(Category)
    store = models.ForeignKey(Store)
    image = models.ImageField(upload_to="images")
    image_thumbnail = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(300,200)], options={"quality":80}, cache_to="regular")
    image_thumbnail_mini = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(100,80)], options={"quality":60}, cache_to="mini")
    image_thumbnail_large = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(575,315)], options={"quality":80}, cache_to="large")
    
    date_created = models.DateTimeField(auto_now=True, editable=False)
    
    is_featured= models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag)
    
    objects = ProductManager() #defaultManager
    
    class Meta:
        unique_together =("name","store",)
        ordering = ["-date_created"]
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("imly_product_detail", (), {"store_slug": self.store.slug,
                                            "slug":self.slug})
    
    def get_price(self, *args, **kwargs):
        return self
    
    def handle_order_item(self, orderitem):
        ProductBase.handle_order_item(self, orderitem)
        PriceBase.handle_order_item(self, orderitem)
        
    def save(self, *args, **kwargs):
        if self.description:
            self.description_html = markdown(self.description)
        super(Product, self).save(*args, **kwargs)
        
@receiver(post_save, sender=Product)
def add_category(sender,instance, **kwargs):
    instance.store.categories.add(instance.category)
        
@receiver(post_delete, sender=Product)
def delete_category(sender,instance, **kwargs):
    if instance.store.product_set.filter(category=instance.category):
        return
    else:
        instance.store.categories.remove(instance.category)
        