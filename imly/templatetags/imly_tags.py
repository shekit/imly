from django import template
from imly.models import Category, Tag, Location, Store, Product

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

