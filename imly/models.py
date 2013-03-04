from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    
    name = models.CharField(max_length=50)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class Location(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class Store(models.Model):
    #Store Details
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.OneToOneField(User)
    description = models.TextField()
    
    #metadata
    categories = models.ManyToManyField(Category)
    delivery_areas = models.ManyToManyField(Location)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    #status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return "%s by %s" % (self.name, self.owner)
    
class Product(models.Model):
    #Product Details
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    capacity_per_month = models.IntegerField()
    price = models.IntegerField()
    lead_time = models.IntegerField(default=1)
    category = models.ForeignKey(Category)
    store = models.ForeignKey(Store)
    product_image = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    
    is_featured= models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    
    class Meta:
        unique_together =("name","store",)
    
    def __unicode__(self):
        return "%s in store %s" % (self.name, self.store.name)