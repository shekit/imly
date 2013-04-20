import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from plata.product.models import ProductBase
from plata.shop.models import PriceBase, Order, TaxClass
from plata.product.stock.models import Period, StockTransaction
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdown import markdown
import uuid
from imly.managers import StoreManager, ProductManager
from imly_project.settings import PROJECT_DIR
from imly_project import settings

from django.contrib.contenttypes import generic
from reviews.models import ReviewedItem

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
    return os.path.join("large", path)

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
    store_contact_number = models.CharField(max_length=10, verbose_name="Contact Number",
                                            help_text="(Mobile number) We will not share this with anyone")
    description = models.TextField()
    description_html = models.TextField(editable=False, blank=True)
    tagline = models.CharField(max_length=255, blank=True, help_text="(optional)")
    
    #metadata
    categories = models.ManyToManyField(Category, blank=True)
    pick_up = models.BooleanField(default=False)
    pick_up_address = models.TextField(blank=True)
    pick_up_location = models.CharField(max_length=50,blank=True)
    provide_delivery = models.BooleanField(default=False)
    delivery_areas = models.ManyToManyField(Location, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True)
    
    #promotion
    facebook_link = models.URLField(blank=True, help_text="(optional)")
    twitter_link = models.URLField(blank=True, help_text="(optional)")
    
    #status
    store_notice = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    tags = models.ManyToManyField(Tag, blank=True)
    
    objects = StoreManager()  # default manager
    
    
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

    def reset_tags(self):
      self.tags.clear()
      self.tags.add(*Tag.objects.filter(product__in=self.product_set.all()))

    def reset_categories(self):
      self.categories.clear()
      self.categories.add(*Category.objects.filter(product__in = self.product_set.all()))
      
class Product(ProductBase, PriceBase):
    #Product Details
    HOUR = 1
    DAY = 2
    LEAD_TIME_CHOICES = (
        (HOUR, "hour"),
        (DAY, "day"),
    )
    
    PIECES = 1
    SERVING = 2
    GRAMS = 3
    KILOS = 4
    QUANTITY_BY_PRICE = (
        (PIECES,"piece"),
        (SERVING, "serving"),
        (GRAMS, "gram"),
        (KILOS,"kg"),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    quantity_per_item = models.IntegerField(default=1)
    quantity_by_price = models.IntegerField(choices=QUANTITY_BY_PRICE,default=PIECES)
    capacity_per_day = models.IntegerField(help_text="How many can you make every month?")
    previous_cpd = models.IntegerField(default=0)
    items_in_stock = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default = False)
    description = models.TextField(blank=True,help_text="(optional)")
    description_html = models.TextField(editable=False, blank=True)
    lead_time = models.IntegerField(default=1,help_text="(in days)")
    lead_time_unit = models.IntegerField(choices=LEAD_TIME_CHOICES, default=DAY)
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
    
    objects = ProductManager() #defaultManager
    
    reviews = generic.GenericRelation(ReviewedItem)
    
    class Meta:
        unique_together =("name","store",)
        ordering = ["-date_created"]
    
    def __unicode__(self):
        return "%s by %s" % (self.name, self.store.name)
    
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
        # setting the capacity of product on change of capacity per day
        transaction_type = change = None # using this approach so that stock transactions can be created after new products being created
        if self.capacity_per_day != self.previous_cpd:
            change = self.capacity_per_day - self.previous_cpd
            if self.capacity_per_day < self.previous_cpd - self.items_in_stock:
                self.capacity_per_day = self.previous_cpd - self.items_in_stock
            self.previous_cpd = self.capacity_per_day
            transaction_type = self.pk and StockTransaction.CORRECTION or StockTransaction.INITIAL
        if self.description:
            self.description_html = markdown(self.description)
        self.slug = "%s-%s" % (self.store.slug, slugify(self.name))
        self.currency = settings.CURRENCIES[0]
        self.tax_class = TaxClass.objects.get(name="India")
        #self.items_in_stock = self.capacity_per_month
        super(Product, self).save(*args, **kwargs)
        if change:
            self.stock_transactions.create(period=Period.objects.current(), type=transaction_type, change=change)
            self.stock_transactions.items_in_stock(self, update=True)

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
