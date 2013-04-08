import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.mail import send_mail
from plata.product.models import ProductBase
#from plata.product.stock.models import Period, StockTransaction
from plata.shop.models import PriceBase, Order, TaxClass
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdown import markdown
import uuid
from imly.managers import StoreManager, ProductManager
from imly_project.settings import PROJECT_DIR
from imly_project import settings
from djangoratings.fields import RatingField


def get_image_path(instance,filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    store_name = instance.store.slug
    return os.path.join("images",store_name, filename)

def get_thumbnail_path(instance,path,specname,extension):
    return os.path.join("regular",path)

def get_thumbnail_mini_path(instance,path,specname,extension):
    return os.path.join("mini", path)

def get_thumbnail_large_path(instance,path,specname,extension):
    return os.path.join("large",path)

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
    tagline = models.CharField(max_length=255, blank=True, help_text="(optional)")
    
    #metadata
    categories = models.ManyToManyField(Category, blank=True)
    delivery_areas = models.ManyToManyField(Location)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True)
    
    #status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    tags = models.ManyToManyField(Tag, blank=True)
    
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
        self.slug = slugify(self.name)
        super(Store, self).save(*args, **kwargs)

    def reassign_product_tags(self):
      self.tags.clear()
      self.tags.add(*Tag.objects.filter(product__in=self.product_set.all()))

    def reassign_product_categories(self):
      self.categories.clear()
      self.categories.add(*Category.objects.filter(product__in=self.product_set.all()))
      
class Product(ProductBase, PriceBase):
    #Product Details
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    capacity_per_month = models.IntegerField(help_text="How many can you make every month?")
    items_in_stock = models.IntegerField(default=0)
    description = models.TextField(blank=True,help_text="(optional)")
    description_html = models.TextField(editable=False, blank=True)
    items_in_stock = models.IntegerField(default=0)
    lead_time = models.IntegerField(default=1,help_text="(in days)")
    category = models.ForeignKey(Category)
    store = models.ForeignKey(Store)
    image = models.ImageField(upload_to=get_image_path, help_text="Minimum image size - 600 X 340 pixels")
    image_thumbnail = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(300,200)], options={"quality":80}, cache_to=get_thumbnail_path)
    image_thumbnail_mini = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(100,80)], options={"quality":60}, cache_to=get_thumbnail_mini_path)
    image_thumbnail_large = ImageSpecField(image_field="image", format="JPEG", processors = [ResizeToFill(575,315)], options={"quality":80}, cache_to=get_thumbnail_large_path)
    
    date_created = models.DateTimeField(auto_now=True, editable=False)
    
    is_featured= models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag)
    
    rating = RatingField(range=5)
    
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
        self.slug = "%s-%s" % (self.store.slug, slugify(self.name))
        self.currency = settings.CURRENCIES[0]
        self.tax_class = TaxClass.objects.get(name="India")
        super(Product, self).save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    about_me = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars", blank=True)
    avatar_thumbnail = ImageSpecField(image_field="avatar", format="JPEG", processors = [ResizeToFill(150,150)], options={"quality":70}, cache_to="avatar_regular")
    avatar_thumbnail_mini = ImageSpecField(image_field="avatar", format="JPEG", processors = [ResizeToFill(50,50)], options={"quality":60}, cache_to="avatar_mini")

    def __unicode__(self):
        return self.first_name

    def get_image(self):
        if not self.avatar:
            self.avatar = os.path.join(PROJECT_DIR,"/media/images/image.jpg")
            return self.avatar

@receiver(m2m_changed, sender=Product.tags.through)
def update_store_tags_from_product(sender, instance, action, **kwargs):
  if action == 'post_add':
    # simple approach
    instance.store.reassign_product_tags()
      
@receiver(post_save, sender=Product)
def update_store_categories_from_product(sender, instance, **kwargs):
    instance.store.reassign_product_categories()

@receiver(post_delete, sender=Product)
def update_store_tags_and_categories_from_product(sender, instance, **kwargs):
  instance.store.reassign_product_tags()
  instance.store.reassign_product_categories()

@receiver(post_save, sender=Store)
def send_store_mail(sender,instance,created, **kwargs):
    if created:
        send_mail("Store added - Awaiting Confirmation","Store has been added by %s" % (instance.owner), instance.owner.email , ["imlyfood@gmail.com"], fail_silently=False)
        