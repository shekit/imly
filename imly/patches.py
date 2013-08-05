from plata.shop.forms import BaseCheckoutForm

def patched_base_checkout_form_clean(self):
    return super(BaseCheckoutForm, self).clean()
