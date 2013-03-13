from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from imly.models import Product, Store, Category

@receiver(post_save, sender="Product")
def add_category(sender, **kwargs):
    sender.store.categories.add(sender.category)
        
@receiver(post_delete, sender="Product")
def delete_category(sender, **kwargs):
    if sender.store.product_set.filter(category=sender.category):
        return
    else:
        sender.store.categories.remove(sender.category)