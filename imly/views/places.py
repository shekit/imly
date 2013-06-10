from imly.models import Location, City
from django.shortcuts import get_object_or_404, redirect, render
from imly.utils import geocode

def set_location(request):
    try:
        place_slug = request.GET.get('location', 'all')        
        result = geocode(place_slug)
        if result: 
            request.session['bingeo'] = result[1]
            display_place_slug = place_slug.split(",")[0]
            request.session["place_slug"], request.session["display_place_slug"] = place_slug, display_place_slug
        else:
            return redirect("/no-such-place/")            
        if "/no-such-place/" in request.referer:
            return redirect("/food/")
    except IndexError:
        return redirect("/no-such-place/")
    return redirect(request.GET.get("next", request.referer))

def unset_location(request):
    try:
        request.session.pop("place_slug")
        request.session.pop("display_place_slug")
        request.session.pop("bingeo")
    except KeyError:
        pass
    return redirect(request.referer)
    
    
def set_city(request):
    try:
        city_slug = request.GET.get('city', None)
        city = City.objects.get(slug=city_slug)
    except:
        pass
    request.session['city'] = city_slug
    return redirect(request.GET.get("next", request.referer))
