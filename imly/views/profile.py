from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext, Context
from imly.forms import UserProfileForm, ChefTipForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from imly.models import Product, Category, Store, Tag, Location, UserProfile
from plata.shop.models import Order, OrderItem
from django.core.exceptions import ValidationError
from allauth.account.forms import LoginForm, SignupForm
from allauth.account.utils import complete_signup
    
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

class ChefProfile(DetailView):
    model = UserProfile
    template_name = "chef_profile.html"
    
    def get_queryset(self):
        return UserProfile.objects.filter(user__in=User.objects.filter(store__in=Store.objects.is_approved().all()))
        
            
    
    
class ProfileList(ListView):
    model = UserProfile
    template_name = "imly_profiles.html"
    paginate_by = 12
    
    def get_queryset(self):
        return UserProfile.objects.filter(user__in=User.objects.filter(store__in=Store.objects.is_approved().all())).exclude(cover_profile_image=None)
        

            

class ProfileCreate(CreateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_create_profile.html"
    success_url = "/account/my-profile/"
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(ProfileCreate,self).form_valid(form)


class EditProfile(UpdateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_edit_profile.html"
    success_url = "/account/my-profile/"

    def get(self,request,*args,**kwargs):
        if self.get_object().user == self.request.user:
            return super(EditProfile,self).get(request,*args,**kwargs)
        else:
            return HttpResponseForbidden()

    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)


def give_us_tip(request):
    if request.method == 'POST':
        tip_form = ChefTipForm(request.POST)
        if tip_form.is_valid():
            tip_form.save()
            return HttpResponse("Submitted")
        response = render(request,"tip.html",locals())
        response.status_code = 400 
        return response
    
def modal_login(request, **kwargs):
    
   # redirect_field_name = kwargs.pop("next")
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            next = request.POST.get("next","/food/")
            login_form.login(request, redirect_url=next)
            print next
            return HttpResponse(next)
        redirect_field_name, redirect_field_value = "next", request.META["HTTP_REFERER"]
        response = render(request,"login_error.html",locals())
        response.status_code = 400 
        return response
    
def modal_signup(request, **kwargs):
    
    if request.method == "POST":
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save(request)
            next = request.POST.get("next","/food/")
            complete_signup(request, user, "/food/")
            return HttpResponse(next)
        redirect_field_name, redirect_field_value = "next", request.META["HTTP_REFERER"]
        response = render(request, "signup_error.html", locals())
        response.status_code = 400
        return response
