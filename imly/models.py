from plata.shop.models import Order
import os
from datetime import date
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point, Polygon
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.contenttypes import generic
from plata.fields import JSONField
from plata.product.models import ProductBase
from plata.shop.models import PriceBase, Order, TaxClass
from plata.product.stock.models import Period, StockTransaction
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from reviews.models import ReviewedItem
from markdown import markdown
import uuid
from imly.managers import StoreManager, ProductManager
from imly_project.settings import PROJECT_DIR,STATIC_ROOT
from imly_project import settings

def get_image(instance,filename):
    if instance.avatar:
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        store_name = instance.user.store.slug
        return os.path.join("images",store_name, filename)
    #else:
     #   return os.path.join(STATIC_ROOT,"/star-rating/image.jpg")


def get_image_path(instance,filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    store_name = instance.store.slug
    return os.path.join("images",store_name, filename)

def get_store_image_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    store_name = instance.slug
    return os.path.join("store-logos",store_name, filename)

def get_cover_image_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    store_name = instance.slug
    return os.path.join("cover-photos",store_name, filename)

def get_store_logo_path(instance, path, specname, extension):
    return os.path.join("logos", path)

def get_store_cover_photo_path(instance, path, specname, extension):
    return os.path.join("cover-photos", path)

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

class Store(geo_models.Model):
    #Store Details
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.OneToOneField(User)
    store_contact_number = models.CharField(max_length=10, verbose_name="Contact Number",
                                            help_text="(Mobile number) We will not share this with anyone")
    description = models.TextField()
    description_html = models.TextField(editable=False, blank=True)
    tagline = models.CharField(max_length=255, blank=True, help_text="(optional)")
    logo = models.ImageField(upload_to=get_store_image_path,blank=True, help_text="(optional)")
    logo_thumbnail = ImageSpecField(image_field="logo", format="JPEG",processors = [ResizeToFill(300,200)], cache_to=get_store_logo_path)
    cover_photo = models.ImageField(upload_to=get_cover_image_path, blank=True, help_text="(optional) Recommended Size - 900 X 250")
    cover_photo_thumbnail = ImageSpecField(image_field="cover_photo", format="JPEG",cache_to=get_store_cover_photo_path)
    
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
    is_open = models.BooleanField(default=True)
    store_notice = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    orders = models.ManyToManyField(Order, through='StoreOrder')
    tags = models.ManyToManyField(Tag, blank=True)
    delivery_points = geo_models.MultiPointField(default="MULTIPOINT(72.8258 18.9647)")
    
    geo_objects = geo_models.GeoManager()
    objects = StoreManager()  # default manager
    everything = models.Manager()
    
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
        return super(Store, self).save(*args, **kwargs)

    def reset_tags(self):
      self.tags.clear()
      self.tags.add(*Tag.objects.filter(product__in=self.product_set.all()))

    def reset_categories(self):
      self.categories.clear()
      self.categories.add(*Category.objects.filter(product__in = self.product_set.all()))

class DeliveryLocation(geo_models.Model):
    name = geo_models.CharField(max_length=100)
    store = geo_models.ForeignKey(Store,blank=True, related_name='delivery_locations')
    location = geo_models.PointField(default="POINT(72.8258 18.9647)", blank=True)    
    bounds = geo_models.PolygonField(default=Polygon.from_bbox((19.26952240, 72.98005230, 18.89330870, 72.77590560)).wkt, blank=True)
    data = JSONField(blank=True, help_text="JSON encoded data collected from google", default="{}")
    
    objects = geo_models.GeoManager()

    def __unicode__(self):
        return self.name
        
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
    DOZEN = 5
    QUANTITY_BY_PRICE = (
        (PIECES,"piece"),
        (SERVING, "serving"),
        (GRAMS, "gram"),
        (KILOS,"kg"),
        (DOZEN,"dozen"),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    quantity_per_item = models.IntegerField(default=1)
    quantity_by_price = models.IntegerField(choices=QUANTITY_BY_PRICE,default=PIECES)
    capacity_per_day = models.IntegerField(help_text="How many can you make every day?")
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
    position = models.PositiveIntegerField(default=0)
    
    objects = ProductManager() #defaultManager
    everything = models.Manager()
    reviews = generic.GenericRelation(ReviewedItem)
    
    class Meta:
        unique_together =("name","store",)
        ordering = ["position","store"]
    
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

    @property
    def is_approved(self):
        return self.store.is_approved
        
    @property
    def sale(self):
        return self.capacity_per_day - self.items_in_stock

    def save(self, *args, **kwargs):
        # setting the capacity of product on change of capacity per day
        # using this approach so that stock transactions can be created after new products being created
        if not self.pk:
            product_count = Product.objects.filter(is_deleted = False)
            self.position = product_count + 1
            print self.position
        transaction_type = change = None
        if self.capacity_per_day != self.previous_cpd:  # managing the stock for current product
            # if new capacity is less than sales than adjust items in stock to make it zero
            # else update it to the new difference
            change = self.capacity_per_day < self.previous_cpd - self.items_in_stock and -self.items_in_stock or self.capacity_per_day - self.previous_cpd
            self.previous_cpd = self.capacity_per_day
            transaction_type = self.pk and StockTransaction.CORRECTION or StockTransaction.INITIAL
        if self.description:
            self.description_html = markdown(self.description)
        self.slug = "%s-%s" % (self.store.slug, slugify(self.name))
        self.currency = settings.CURRENCIES[0]
        self.tax_class = TaxClass.objects.get(name="India")
        super(Product, self).save(*args, **kwargs)
        if change:  # continued managing stock for the product
            self.stock_transactions.create(period=Period.objects.current(), type=transaction_type, change=change)
            self.stock_transactions.items_in_stock(self, update=True)

class StoreOrder(models.Model):
    store = models.ForeignKey(Store)
    order = models.ForeignKey(Order)
    delivered_on = models.DateTimeField(default=date.today())
    store_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    created = models.DateTimeField(auto_now = True)
    updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.store.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField()
    about_me = models.TextField(blank=True)
    about_me_html = models.TextField(editable=False, blank=True)
    cover_profile_image = models.ImageField(upload_to=get_image, blank=True)
    cover_profile_image_thumbnail = ImageSpecField(image_field="cover_profile_image", format="JPEG", cache_to="cover_profile_regular")
    word_one = models.CharField(max_length=40, blank=True)
    word_two = models.CharField(max_length=40, blank=True)
    word_three = models.CharField(max_length=40, blank=True)
    avatar = models.ImageField(upload_to=get_image, blank=True)
    avatar_thumbnail = ImageSpecField(image_field="avatar", format="JPEG", processors = [ResizeToFill(150,150)], options={"quality":70}, cache_to="avatar_regular")
    avatar_thumbnail_mini = ImageSpecField(image_field="avatar", format="JPEG", processors = [ResizeToFill(50,50)], options={"quality":60}, cache_to="avatar_mini")

    def __unicode__(self):
        return self.first_name

    def save(self, *args, **kwargs):
        if self.about_me:
            self.about_me_html = markdown(self.about_me)
        if self.first_name:
            self.slug = "%s-%s" % (self.first_name.lower(), self.last_name.lower())
        super(UserProfile,self).save(*args, **kwargs)
    
class ChefTip(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Chef's Name")
    tip_contact_number = models.CharField(max_length = 10, verbose_name = "Chef's Number")
    #description = models.CharField(max_length=100, verbose_name="Chef's Speciality")
    your_name = models.CharField(max_length = 100, verbose_name = "Your Name", blank=True)
    #email = models.EmailField(max_length = 50, verbose_name = "Your Email")
    create = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.name
