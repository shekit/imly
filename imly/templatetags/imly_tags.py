from django import template
from django.contrib.gis.geos import Point
from imly.models import Category, Tag, Location, Store, Product
from django.contrib.gis.measure import D
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
        context["categories"] = Category.objects.filter(super_category=None)
        return ""
    

def do_tag_list(parser, token):
    return TagListNode()

class TagListNode(template.Node):
    
    def render(self,context):
        #selected_tags = context.get("selected_tags",[])
        selected_tags = context['request'].session.get("tags",[])
        if selected_tags:
            context["tags"] = Tag.objects.exclude(slug__in=selected_tags)
        else:
            context["tags"] = Tag.objects.all()
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
            user_geo=session['bingeo']
            user_point = Point(*user_geo)

            distance = Store.objects.filter(pk=store.pk).distance(user_point, field_name='delivery_points')[0].distance
            self.store.delivers = distance.km < D(km=3)
            return ''

        else :
            store.delivers = False
            #raise template.TemplateSyntaxError('Not enough data for generating this information')

def do_store_delivers(parser, token):
    try:
        tag_name, store = token.split_contents()
        isinstance(store, Store)
    except ValueError:
        raise template.TemplateSyntaxError('store_delivers requires store')
    return StoreDeliversNode(store)
    
register.tag('store_delivers', do_store_delivers)

class DeliveryLeadOptionsNode(template.Node):
    def render(self, context):
        pass
        
def do_delivery_lead_options(parser, token):
    return DeliveryLeadOptionsNode()
    
register.tag('delivery_lead_options', do_delivery_lead_options)

@register.inclusion_tag('imly/delivery_lead_options.html')
def delivery_lead_options(store):
    return {'choices': ((1, "Hi ya"), (2, "See yaa"))}
    

class OrderTimeOptionsNode(template.Node):
    def render(self, context):
        pass
        
def do_order_time_options(parser, token):
    return DeliveryLeadOptionsNode()
    
register.tag('order_time_options', do_order_time_options)

class PickUpChoiceNode(template.Node):
    def render(self, context):
        pass
        
def do_pick_up_choice(parser, token):
    return DeliveryLeadOptionsNode()
    
register.tag('pick_up_choice', do_pick_up_choice)

class DeliveryChoiceNode(template.Node):
    def render(self, context):
        pass
        
def do_delivery_choice(parser, token):
    return DeliveryLeadOptionsNode()
    
register.tag('delivery_choice', do_delivery_choice)

    
