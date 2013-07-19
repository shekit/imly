from plata.shop.models import Order
import os
from datetime import date, timedelta, datetime
from django.db.models import Sum, Max
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
from imly.managers import StoreManager, ProductManager, SpecialManager
from imly.utils import geocode
from plata.shop.models import OrderItem
from imly_project.settings import PROJECT_DIR,STATIC_ROOT
from imly_project import settings
from plata.fields import JSONField
from autoslug import AutoSlugField
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail,EmailMessage,get_connection

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
    product_ordering = models.IntegerField(default=10)
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

    def flag_product(self):
        return self.product_set.filter(is_flag = True).count() == 1 and self.product_set.count() == 1

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
    slug = AutoSlugField(populate_from='name', editable=True, unique=True)
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
    pick_up = models.BooleanField(default=True)
    pick_up_address = models.TextField()
    pick_up_location = models.CharField(max_length=255)
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
        return super(Store, self).save(*args, **kwargs)

    def delivers_to(self):
        return ', '.join([dl.display for dl in self.delivery_locations.all()])
    def reset_tags(self):
        for tag in self.tags.all():
            if not tag.product_set.count():
                tag.is_active = False
            tag.save()
        self.tags.clear()
        self.tags.add(*Tag.objects.filter(product__in=self.product_set.all()))
        for tag in self.tags.all():
            if tag.product_set.count():
                tag.is_active = True
            tag.save()

    def reset_categories(self):
        for cat in self.categories.all():
            if not cat.product_set.count():
                cat.is_active = False
                cat.super_category.is_active = False
            cat.save()
            cat.super_category.save()
        self.categories.clear()
        self.categories.add(*Category.objects.filter(product__in = self.product_set.all()))
        for cat in self.categories.all():
            if cat.product_set.count():
                cat.is_active = True
                cat.super_category.is_active = True
            cat.save()
            cat.super_category.save()

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
        #(HOUR, "hour"),
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
    slug = AutoSlugField(populate_from='name', unique_with=['store__name', 'name'], editable=True)
    quantity_per_item = models.DecimalField(default=1, max_digits=6,decimal_places=2)
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
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)
    is_featured= models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    is_flag = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)
    pick_up_point = geo_models.PointField(null=True, blank=True)
    delivery_points = geo_models.MultiPointField(null=True, blank=True)
    is_veg = models.BooleanField(default=True)
    objects = ProductManager() #defaultManager
    everything = models.Manager()
    reviews = generic.GenericRelation(ReviewedItem)
    data = JSONField('data',blank=True,help_text="JSON-encoded additional data about the store.")

    class Meta:
        unique_together =("name","store",)
        ordering = ['category__product_ordering', 'position']
    
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

    def stock_change(self,order):
        try:
            order_item = order.items.get(product=self)
            return self.items_in_stock - order_item.quantity
        except OrderItem.DoesNotExist:
            return self.items_in_stock


    def save(self, *args, **kwargs):
        # setting the capacity of product on change of capacity per day
        # using this approach so that stock transactions can be created after new products being created
        if self.is_flag and not self.data.get('flag',''):
            self.position = Product.objects.filter(store=self.store).count() + 20
            self.flag_reason = "Please upload a better quality image for this dish"
            self.data['flag'],self.data['date'],self.data['time'] = 'True',datetime.today().date(),datetime.today().time()
             
        if not self.is_flag and self.data.get('flag',''):
            self.position = Product.objects.filter(is_deleted = False, store=self.store).count() + 1
            self.flag_reason = ''
            self.data['flag'] = ''
            self.data['date'] = ''
            self.data['time'] = ''
            
        if not self.pk:
            self.position = Product.objects.filter(is_deleted = False, store=self.store).count()
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
        
        
        (1, ('12pm - 1pm')),
        (2, ('1pm - 2pm')),
        (3, ('2pm - 3pm')),
        (4, ('3pm - 4pm')),
        (5, ('4pm - 5pm')),
        (6, ('5pm - 6pm')),
        (7, ('6pm - 7pm')),
        (8, ('Anytime')),
        )
    
    store = models.ForeignKey(Store)
    order = models.ForeignKey(Order)
    delivered_on = models.DateTimeField(default=date.today())
    delivered_by_product_lead = models.DateTimeField(default=date.today())
    delivery_lead = models.IntegerField(default=0) 
    delivery_charges = models.IntegerField(default=0)
    order_time = models.IntegerField(choices= TimeChoices, default=3)
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
    
    @classmethod
    def update_for_order(cls, instance):
        stores = set((item.product.store for item in instance.items.all()))
        StoreOrder.objects.filter(order=instance).exclude(store__in=stores).delete()
        for store in stores:
            store_order, created = StoreOrder.objects.get_or_create(store=store,order=instance)
            store_order.delivered_by_product_lead = (instance.created.date() > datetime.now().date() and instance.created or datetime.now()) + timedelta(days=instance.items.filter(product__in=store.product_set.all()).aggregate(max = Max('product__lead_time'))['max'])
    #        store_order.delivered_by_product_lead = instance.created + timedelta(days=instance.items.filter(product__in=store.product_set.all()).aggregate(max = Max('product__lead_time'))['max'])
            store_order.store_total = sum((item.subtotal for item in instance.items.filter(product__in=store.product_set.all())))
            store_order.store_items = instance.items.filter(product__in=store.product_set.all()).count()
            store_order.save()
    
        
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

class City(geo_models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name')
    enclosing_geometry = geo_models.PolygonField(blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def default():
        return City.objects.get(slug="mumbai")

class Special(models.Model):
    title = models.CharField(max_length = 100)
    slug = AutoSlugField(populate_from = 'title')
    active = models.BooleanField(default = True)
    live = models.BooleanField(default = False)
    chef_can_tag = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True)
    priority = models.IntegerField(default = 10)
    created = models.DateTimeField(auto_now_add = True)

    special_cover_photo = models.ImageField(upload_to="special-cover-photos", blank=True)
    special_cover_photo_thumbnail_mini = ImageSpecField(image_field="special_cover_photo", format="JPEG",options={'quality': 92}, processors = [ResizeToFill(768,200)], cache_to="special-cover-photo-thumbnails-mini")
    
    special_button_photo = models.ImageField(upload_to="special-button-photo", blank=True)
    

    objects = SpecialManager()

    def __unicode__(self):
        return self.title
        
