from plata.shop.forms import BaseCheckoutForm

def patched_base_checkout_form_clean(self):
        data = super(BaseCheckoutForm, self).clean()
        email = data.get('email')
        create_account = data.get('create_account')
        if email:
            users = list(User.objects.filter(email=email))
            if create_account and users and self.request.user not in users:
                self._errors['email'] = self.error_class([
                            _('This e-mail address belongs to a different account.')])
        return data
