from forms import ChefTipForm
from allauth.account.forms import LoginForm, SignupForm

def chef_tip(request):
	return {'tip_form': ChefTipForm()}

def modal_signup(request):
	return {
		"login_form": LoginForm(),
		"signup_form" : SignupForm(),
	}