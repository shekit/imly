from imly.models import Tag
from django.shortcuts import get_object_or_404, redirect, render

def add_tag(request, slug):
    if request.session.get('tags',None):
        tags = request.session['tags']
        tags.append(slug)
        request.session['tags'] = tags
    else:
        request.session['tags']=[slug]
    return redirect(request.referer.split('?')[0])


def remove_tag(request, slug):
    tag_list = request.session["tags"]
    tag_list.remove(slug)
    request.session["tags"] = tag_list
    #raise Exception(request.session["tags"])
    return redirect(request.referer.split('?')[0])