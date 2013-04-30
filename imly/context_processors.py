from forms import ChefTipForm

def chef_tip(request):
	return {'tip_form': ChefTipForm()}
