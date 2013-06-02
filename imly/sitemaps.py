from django.contrib.sitemaps import GenericSitemap

from models import Store, Product, Category

all_sitemaps = {}

for store in Store.objects.filter(is_approved=True):
    all_sitemaps[store.name] = GenericSitemap({'queryset': store.product_set.is_approved().filter(is_deleted=False)}, priority=0.6)
