from forms import ChefTipForm
from allauth.account.forms import LoginForm, SignupForm
from imly.models import City

def chef_tip(request):
	return {'tip_form': ChefTipForm()}

def modal_signup(request):
	return {
		"login_form": LoginForm(),
		"signup_form" : SignupForm(),
	}

def select_city(request):
	return {"cities":City.objects.all()}