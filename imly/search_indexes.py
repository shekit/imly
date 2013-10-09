from haystack import indexes
from haystack.fields import LocationField
from haystack.utils.geo import Point

from .models import Product, Store


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    store = indexes.CharField(model_attr='store')
    category = indexes.CharField(model_attr='category')
    pick_up_location = indexes.LocationField(model_attr='pick_up_point', null=True)
    delivery_locations = indexes.LocationField()
    
    def get_model(self):
        return Product
        
    def index_queryset(self, using=None):
        return Product.objects.all()
    
    def prepare_delivery_locations(self, obj):
        return obj.store.delivery_locations.exists() and [{'lat': delivery.location.get_y(), 'lon': delivery.location.get_x()} for delivery in obj.store.delivery_locations.all()] or None