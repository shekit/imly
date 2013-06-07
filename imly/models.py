from plata.shop.models import Order
import os
from datetime import date, timedelta
from django.db.models import Sum
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point, Polygon, MultiPoint
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.contenttypes import generic
from plata.fields import JSONField
from plata.product.models import ProductBase
from plata.shop.models import PriceBase, Order, TaxClass
from plata.product.stock.models import Period, StockTransaction
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill,SmartResize, ResizeToFit
from reviews.models import ReviewedItem
from markdown import markdown
import uuid
from imly.managers import StoreManager, ProductManager
from imly.utils import geocode
from imly_project.settings import PROJECT_DIR,STATIC_ROOT
from imly_project import settings
from plata.fields import JSONField
from autoslug import AutoSlugField

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
    slug = AutoSlugField(populate_from='name')
    owner = models.OneToOneField(User)
    store_contact_number = models.CharField(max_length=10, verbose_name="Contact Number",
                                            help_text="(Mobile number) We will not share this with anyone")
    description = models.TextField()
    description_html = models.TextField(editable=False, blank=True)
    tagline = models.CharField(max_length=255, blank=True, help_text="(optional)")
    logo = models.ImageField(upload_to=get_store_image_path,blank=True, help_text="(optional)")
    logo_thumbnail = ImageSpecField(image_field="logo", format="JPEG",options={'quality': 92},processors = [ResizeToFill(300,200)], cache_to=get_store_logo_path)
    cover_photo = models.ImageField(upload_to=get_cover_image_path, blank=True, help_text="(optional) Recommended Size - 900 X 250")
    cover_photo_thumbnail = ImageSpecField(image_field="cover_photo", format="JPEG",options={'quality': 92}, processors = [ResizeToFill(900,200)], cache_to=get_store_cover_photo_path)
    
    #metadata
    categories = models.ManyToManyField(Category, blank=True)
    pick_up = models.BooleanField(default=False)
    pick_up_address = models.TextField(blank=True)
    pick_up_location = models.CharField(max_length=255,blank=True)
    pick_up_landmark = models.CharField(max_length=100,blank=True)
    pick_up_point = geo_models.PointField(null=True, blank=True)
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
    delivery_points = geo_models.MultiPointField(blank=True, null=True)
    data = JSONField('data',blank=True,help_text="JSON-encoded additional data about the store.")
    
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
        if self.pick_up_location:
            result = geocode(self.pick_up_location)
            if result: self.pick_up_point = Point(*result[1]) 
        if self.delivery_locations.count() > 0 and not self.delivery_points: # counts on approval to store locations
            self.delivery_points = MultiPoint(*(dl.location for dl in self.delivery_locations.all()))
        return super(Store, self).save(*args, **kwargs)

    def delivers_to(self):
        return ', '.join([dl.display for dl in self.delivery_locations.all()])
    def reset_tags(self):
      self.tags.clear()
      self.tags.add(*Tag.objects.filter(product__in=self.product_set.all()))

    def reset_categories(self):
      self.categories.clear()
      self.categories.add(*Category.objects.filter(product__in = self.product_set.all()))

    @property
    def pick_up_display(self):
        return self.pick_up_location.split(",")[0].title()
    
    @property
    def delivers(self):
        return self._delivers
        
    @delivers.setter
    def delivers(self, value):
        self._delivers = value
        
class DeliveryLocation(geo_models.Model):
    name = geo_models.CharField(max_length=100)
    store = geo_models.ForeignKey(Store,blank=True, related_name='delivery_locations')
    location = geo_models.PointField(null=True, blank=True)    
    objects = geo_models.GeoManager()

    def __unicode__(self):
        return self.name
    
    @property
    def display(self):
        return self.name.split(",")[0].title()

class Product(ProductBase, PriceBase, geo_models.Model):
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
    LITRE = 6
    ML = 7
    QUANTITY_BY_PRICE = (
        (PIECES,"piece"),
        (SERVING, "serving"),
        (GRAMS, "gram"),
        (KILOS,"kg"),
        (DOZEN,"dozen"),
        (LITRE,"litre"),
        (ML,"ml"),
    )
    
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique_with=['store__name', 'name'])
    quantity_per_item = models.IntegerField(default=1)
    quantity_by_price = models.IntegerField(choices=QUANTITY_BY_PRICE,default=PIECES)
    capacity_per_day = models.IntegerField(help_text="How many can you make every day?")
    previous_cpd = models.IntegerField(default=0)
    items_in_stock = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default = False)
    description = models.TextField(blank=True,help_text="(optional)")
    description_html = models.TextField(editable=False, blank=True)
    lead_time = models.IntegerField(default=1,help_text="(in days or hours)")
    lead_time_unit = models.IntegerField(choices=LEAD_TIME_CHOICES, default=DAY)
    category = models.ForeignKey(Category)
    store = models.ForeignKey(Store)
    image = models.ImageField(upload_to=get_image_path, help_text="Minimum 600 pixels wide")
    image_thumbnail = ImageSpecField(image_field="image", format="JPEG",options={'quality': 92}, processors = [ResizeToFill(300,200)], cache_to=get_thumbnail_path)
    image_thumbnail_mini = ImageSpecField(image_field="image", format="JPEG",options={'quality': 92}, processors = [ResizeToFill(100,80)], cache_to=get_thumbnail_mini_path)
    image_thumbnail_large = ImageSpecField(image_field="image", format="JPEG",options={'quality':92}, processors = [ResizeToFit(width=575)], cache_to=get_thumbnail_large_path)
    date_created = models.DateTimeField(auto_now=True, editable=False)
    is_featured= models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    position = models.PositiveIntegerField(default=0)
    pick_up_point = geo_models.PointField(null=True, blank=True)
    delivery_points = geo_models.MultiPointField(null=True, blank=True)
    
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

    def quantity_unit(self):
        return self.QUANTITY_BY_PRICE[self.quantity_by_price - 1][1]
    
    def handle_order_item(self, orderitem):
        ProductBase.handle_order_item(self, orderitem)
        PriceBase.handle_order_item(self, orderitem)

    @property
    def is_approved(self):
        return self.store.is_approved
        
    @property
    def sale(self):
        return abs(self.stock_transactions.filter(type=StockTransaction.SALE).filter(order__status=Order.IMLY_CONFIRMED).aggregate(sale_sum=Sum('change'))['sale_sum'])

    @property
    def store_order_count(self):
        return self.orderitem_set.filter(order__status = Order.IMLY_CONFIRMED).count()

    def save(self, *args, **kwargs):
        # setting the capacity of product on change of capacity per day
        # using this approach so that stock transactions can be created after new products being created
        if not self.pk:
            product_count = Product.objects.filter(is_deleted = False).count()
            if product_count:
                self.position = product_count + 1
            else:
                self.position = 0
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
        self.currency = settings.CURRENCIES[0]
        self.tax_class = TaxClass.objects.get(name="India")
        super(Product, self).save(*args, **kwargs)
        if change:  # continued managing stock for the product
            self.stock_transactions.create(period=Period.objects.current(), type=transaction_type, change=change)
            self.stock_transactions.items_in_stock(self, update=True)

class StoreOrder(models.Model):
    
    TimeChoices = (
        
        
        (1, ('11am - 12pm')),
        (2, ('12pm - 1pm')),
        (3, ('1pm - 2pm')),
        (4, ('2pm - 3pm')),
        (5, ('3pm - 4pm')),
        (6, ('4pm - 5pm')),
        (7, ('5pm - 6pm')),
        (8, ('6pm - 7pm')),
        (9, ('Anytime')),
        )
    
    store = models.ForeignKey(Store)
    order = models.ForeignKey(Order)
    delivered_on = models.DateTimeField(default=date.today())
    delivered_by_product_lead = models.DateTimeField(default=date.today())
    delivery_lead = models.IntegerField(default=0) 
    order_time = models.IntegerField(choices= TimeChoices, default=1)
    pick_up = models.BooleanField(default=True)
    store_total = models.FloatField(default=0.0)
    store_items = models.IntegerField(default=0)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now = True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-delivered_on']
        
    def __unicode__(self):
        return self.store.slug

    def display_order_time(self):
        return self.TimeChoices[self.order_time - 1][1]
        
    def save(self, *args, **kwargs):
        self.delivered_on = self.delivered_by_product_lead + timedelta(days=self.delivery_lead)
        return super(StoreOrder, self).save(*args, **kwargs)
        
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField()
    about_me = models.TextField()
    about_me_html = models.TextField(editable=False, blank=True)
    cover_profile_image = models.ImageField(upload_to=get_cover_image_path, blank=True)
    cover_profile_image_thumbnail = ImageSpecField(image_field="cover_profile_image", format="JPEG", options={'quality': 92},processors = [SmartResize(1600,400)], cache_to="cover_profile_regular")
    word_one = models.CharField(max_length=40)
    word_two = models.CharField(max_length=40)
    word_three = models.CharField(max_length=40)

    is_featured = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.first_name

    def save(self, *args, **kwargs):
        if self.about_me:
            self.about_me_html = markdown(self.about_me)
        if self.first_name:
            self.slug = "%s-%s" % (slugify(self.first_name).lower(), slugify(self.last_name).lower())
        super(UserProfile,self).save(*args, **kwargs)
    
class ChefTip(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Chef's Name")
    tip_contact_number = models.CharField(max_length = 10, verbose_name = "Chef's Number")
    your_name = models.CharField(max_length = 100, verbose_name = "Your Name", blank=True)
    create = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.name
