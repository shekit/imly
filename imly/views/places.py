from imly.models import Location
from django.shortcuts import get_object_or_404, redirect, render

def set_location(request, place_slug):
    request.session["place_slug"] = "" if place_slug == "all" else place_slug
    return redirect(request.GET.get("next", "/products"))