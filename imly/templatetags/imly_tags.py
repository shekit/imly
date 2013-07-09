from django import template
from django.core import urlresolvers
from django.contrib.gis.geos import Point
from imly.models import Category, Tag, Location, Store, Product, StoreOrder, Special
from django.contrib.gis.measure import D
import datetime

def do_featured_store_list(parser, token):
    return FeaturedStoreNode()

class FeaturedStoreNode(template.Node):
    
    def render(self, context):
        context["featured_stores"] = Store.objects.filter(is_featured=True)[:4]
        return ""
        
def do_bestseller_product_list(parser, token):
    return BestsellerProductNode()

class BestsellerProductNode(template.Node):
    
    def render(self, context):
        context["bestselling_products"] = Product.objects.filter(is_bestseller=True)[:4]
        return ""

def do_category_list(parser, token):
    return SuperCategoryNode()

class SuperCategoryNode(template.Node):
    
    def render(self, context):
        #context["categories"] = [category.super_category for category in Category.objects.exclude(super_category=None) if category.product_set.count()]
        context["categories"] = Category.objects.filter(super_category=None).exclude(is_active=False)
        return ""
    

def do_tag_list(parser, token):
    return TagListNode()

class TagListNode(template.Node):
    
    def render(self,context):
        #selected_tags = context.get("selected_tags",[])
        selected_tags = context['request'].session.get("tags",[])
        if selected_tags:
            context["tags"] = Tag.objects.exclude(slug__in=selected_tags,is_active=True)
        else:
            context["tags"] = Tag.objects.all().filter(is_active=True)
        return ""


            
    
def do_location_list(parser,token):
    return LocationListNode()

class LocationListNode(template.Node):
    
    def render(self,context):
        context["locations"] = Location.objects.all()
        return ""
    
def loop_int(value):
    value = int(value)
    return range(value)

register = template.Library()
register.tag("get_category_list", do_category_list)
register.tag("get_tag_list", do_tag_list)
register.tag("get_location_list", do_location_list)
register.tag("get_featured_store_list", do_featured_store_list)
register.tag("get_bestseller_product_list", do_bestseller_product_list)
register.filter("loop_int", loop_int)

# pick up distance tag
class PickupDistanceNode(template.Node):
    
    def __init__(self, store):
        self.store = template.Variable(store)
        
    def render(self, context):
        store = self.store.resolve(context)
        session = context['request'].session
        if session.get('bingeo', None):
            user_geo = session['bingeo']
            user_point = Point(*user_geo)
            return Store.objects.filter(pk=store.pk).distance(user_point)[0].distance.km

        
def do_pick_up_distance(parser, token):
    try:
        tag_name, store = token.split_contents()
        isinstance(store, Store)
    except ValueError:
        raise template.TemplateSyntaxError('pick_up_distance requires store to calculate the distance')
    return PickupDistanceNode(store)
    
register.tag('pick_up_distance', do_pick_up_distance)

# store delivers
class StoreDeliversNode(template.Node):
    
    def __init__(self, store):
        self.store = template.Variable(store)
        
    def render(self, context):
        store = self.store.resolve(context)
        session=context['request'].session
        if session.get('bingeo', None):
            store.delivery_locations.distance(*session['bingeo']).order_by('distance')[0].distance
            self.store.delivers = distance.km < 3
        else:
            self.store.delivers = False
        return self.store.delivers and 'Delivers To You' or ''
    
def do_store_delivers(parser, token):
    try:
        tag_name, store = token.split_contents()
        isinstance(store, Store)
    except ValueError:
        raise template.TemplateSyntaxError('store_delivers requires store')
    return StoreDeliversNode(store)
    
register.tag('store_delivers', do_pick_up_distance)

class StoreAmendGeo(template.Node):
    def __init__(self, store):
        self.store = template.Variable(store)

    def render(self, context):
        store = self.store.resolve(context)
        session = context['request'].session
        store.distance, store.delivers = None, False
        if session.get('bingeo', None):
            user_point = Point(*session['bingeo'])
            store.distance = store.pick_up and Store.objects.filter(pk=store.pk).distance(user_point)[0].distance.km or None            
            try:
                if store.delivery_locations.count():
                    distance = store.delivery_locations.distance(user_point).order_by('distance')[0].distance
                    store.delivers = distance.km < 3
            except AttributeError:
                store.delivers = False
        return ''

def do_store_amend_geo(parser, token):
    try:
        tag_name, store = token.split_contents()
        isinstance(store, Store)
    except ValueError:
        raise template.TemplateSyntaxError('store_amend_geo requires store')
    return StoreAmendGeo(store)

register.tag('store_amend_geo', do_store_amend_geo)

@register.simple_tag(takes_context=True)
def current(context, url_name, return_value="active_top_nav", **kwargs):
    matches = current_url_equals(context,url_name, **kwargs)
    return return_value if matches else ""

def current_url_equals(context, url_name, **kwargs):
    resolved = False
    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except:
        pass
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    return matches

@register.inclusion_tag('imly/store_order_options.html')
def store_order_options(store_order, request):
    return {'store_order': store_order,
            'request': request,
            'delivery_leads': [[day, store_order.delivered_by_product_lead.date() + datetime.timedelta(days=day)] for day in range(15)],
            'time_choices': StoreOrder.TimeChoices
            } 

@register.inclusion_tag('imly/order_item_quantity.html')
def order_item_quantity(order_item):
    return {'orderitem':order_item.quantity * order_item.product.quantity_per_item}

@register.inclusion_tag('special_display.html')
def special_display():
    return {'special': Special.objects.current()}
    
@register.inclusion_tag('imly/quantity_by_price.html')
def quantity_by_price(order_item):
    unit = order_item.quantity * order_item.product.quantity_per_item
    if unit == 1:
        unit = order_item.product.quantity_unit()
    else:
        unit = order_item.product.quantity_unit()+'s'
    return {'quantity_by_price':unit}
    
@register.inclusion_tag('imly/modal_update_cart.html')
def request_update_cart(order):
    if order.created.date() < datetime.datetime.now().date():
        for store_order in order.storeorder_set.all():
            delivered_on_from_today = datetime.datetime.now() + datetime.timedelta(days=store_order.delivery_lead)
            if store_order.delivered_on.date() < delivered_on_from_today.date():
                 return { 'request_update': True, 'order': order }
    return { 'request_update': False }
