from django.http import HttpResponse
from facebook.modules.profile.page.models import Page
from imly.models import Store

def home(request):
    if request.fb_session.signed_request:
        # request is from facebook
        page_info=request.fb_session.signed_request['page']
        if request.GET.get('tabs_added['+page_info['id']+']', None):
            page = Page(id=page_info['id'])
            page.get_from_facebook(save=True)
            store = request.user.store
            store.page=page
            store.save()
            return HttpResponse('imly store just added')
        else:
            page = Page.objects.get(pk=page_info['id'])
            store = Store.objects.get(page=page)
            return HttpResponse('the store is ' + store.name )
    else:
        return HttpResponse('oye, some wanderer on net, get lost you troll')
