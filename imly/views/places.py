from imly.models import Location
from django.shortcuts import get_object_or_404, redirect, render
from omgeo.places import PlaceQuery
from omgeo.services import Bing

def set_location(request):
    place_slug = request.GET.get('location', 'all')
    request.session["place_slug"] = place_slug
    if place_slug in ['all', '']:
        request.session['bingeo'] = None
    else:
        bingeo = Bing(settings={'api_key': 'AgOr3aEARXNVLGGSQe9nt2j6v9ThHyIiSNyWmoO5uw2N5RSfjt3MLBsxB_kgJTFn'})
        pq = PlaceQuery(place_slug)
        result = bingeo.geocode(pq)
        geo = result[0][0]
        request.session['bingeo'] = (geo.x, geo.y) 
    return redirect(request.GET.get("next", "/food"))