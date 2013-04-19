from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Context
from imly.forms import UserProfileForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from imly.models import Product, Category, Store, Tag, Location, UserProfile
from plata.shop.models import Order, OrderItem


class ProfileInfo(DetailView):
    model = UserProfile
    template_name = "imly_my_profile.html"

    '''def get_object(self):
        return get_object_or_404(UserProfile,user=self.request.user)'''

    def get(self,request,*args,**kwargs):
        try:
            self.request.user.userprofile
            return render(request,"imly_my_profile.html",{"object":request.user.userprofile,"user":request.user})
        except UserProfile.DoesNotExist:
            return render(request,"imly_my_profile.html",{"user":request.user})


class ProfileCreate(CreateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_create_profile.html"
    success_url = "/account/my_profile/"
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(ProfileCreate,self).form_valid(form)


class EditProfile(UpdateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_edit_profile.html"
    success_url = "/account/my_profile/"
    
'''    def get(self,request,*args, **kwargs):
        if self.get_object().user != self.request.user:
            return HttpResponseForbidden()
        return super(EditProfile,self).get(request, *args, **kwargs)'''

class UserOrders(ListView):
    model = OrderItem
    template_name = "imly_user_orders.html"

    def get_queryset(self):
        return OrderItem.objects.filter(order__in = self.request.user.orders.all())