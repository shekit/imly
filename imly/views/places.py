from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from imly.models import Location, City, Special
from imly.utils import geocode, tracker

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
            request.session["place_slug"], request.session["display_place_slug"], request.session["delivery"], request.session["pick_up"] = place_slug, display_place_slug , True , False
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
        request.session.pop("delivery")
    except KeyError:
        pass
    try:
        request.session.pop("pick_up")
    except KeyError:
        pass
    return redirect(request.referer)
    
    
def set_city(request, slug):
    try:
        city = City.objects.get(slug=slug)
        tracker.add_event('set-city', {'city': slug})
        if city.slug != request.city and request.session.get('place_slug'):
            request.session.pop("place_slug")
            request.session.pop("display_place_slug")
            request.session.pop("bingeo")
        if 'specials' in request.referer and Special.objects.current():
            return redirect('http://'+city.slug + '.imly.in' + reverse('imly_specials', kwargs={'slug': Special.objects.current().slug}))
        return redirect('http://' + city.slug + '.imly.in/food/')
    except City.DoesNotExist:
        return redirect('http://imly.in/food/')
    except: 
        pass
    if "/will-be-there-soon/" in request.referer:
        return redirect("/food/")
    return redirect(request.GET.get("next", request.referer))

def set_delivery(request):
    try:
        request.session.pop("pick_up")
    except KeyError:
        pass
    request.session["delivery"] = request.path.startswith("/delivery")
    return redirect(request.referer)

def set_pick_up(request):
    try:
        request.session.pop("delivery")
    except KeyError:
        pass
    request.session["pick_up"] = request.path.startswith("/pick-up")
    return redirect(request.referer)
    
