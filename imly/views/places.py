from imly.models import Location, City
from django.shortcuts import get_object_or_404, redirect, render
from imly.utils import geocode, tracker
from django.contrib.gis.geos import Point

def set_location(request):
    try:
        place_slug = request.GET.get('location', 'all')        
        tracker.add_event('set-location', {'location': place_slug})
        result = geocode(place_slug)
        if result: 
            if request.city and not Point(*result[1]).within(request.city.enclosing_geometry):
                return redirect('/not-in-city/')  #redirect if place not within city limits
            request.session['bingeo'] = result[1]
            display_place_slug = place_slug.split(",")[0]
            request.session["place_slug"], request.session["display_place_slug"] = place_slug, display_place_slug
        else:
            return redirect("/no-such-place/")            
        if "/no-such-place/" in request.referer:
            return redirect("/food/")
        if "/not-in-city/" in request.referer:
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
    
    
def set_city(request, slug):
    try:
        city = City.objects.get(slug=slug)
        tracker.add_event('set-city', {'cit': slug})
        if city.slug != request.city and request.session.get('place_slug'):
            request.session.pop("place_slug")
            request.session.pop("display_place_slug")
            request.session.pop("bingeo")
        return redirect('http://' + city.slug + '.imly.in/food/')
    except City.DoesNotExist:
        return redirect('http://imly.in/food/')
    except:
        pass
    if "/will-be-there-soon/" in request.referer:
        return redirect("/food/")
    return redirect(request.GET.get("next", request.referer))
