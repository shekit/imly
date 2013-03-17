from imly.forms import GiveTipForm
from django.views.generic.edit import FormView

class TipView(FormView):
    template_name = "contact.html"
    form_class = GiveTipForm
    success_url = "/thanks/"
    
    def form_valid(self,form):
        form.send_email()
        return super(TipView, self).form_valid(form)