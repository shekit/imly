from imly.models import Recipe, Product
from imly.forms import RecipeForm, RecipeStepForm
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden


class RecipeList(ListView):
    model = Recipe
    template_name = "imly_recipe_list.html"
    
    
class AddRecipe(CreateView):
    form_class = RecipeForm
    model = Recipe
    template_name = "imly_recipe_add.html"
    success_url = "/account/store/products/"
    
    def get_context_data(self, **kwargs):
        context = super(AddRecipe, self).get_context_data(**kwargs)
        if self.request.POST:
            context["recipe_step_form"] = RecipeStepForm(self.request.POST)
        else:
            context["recipe_step_form"] = RecipeStepForm()
        return context
    
class EditRecipe(UpdateView):
    form_class = RecipeForm
    model = Recipe
    template_name = "imly_recipe_edit.html"
    success_url = "/account/store/products/"
    
    def get(self, request, *args, **kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(EditRecipe,self).get(*args, **kwargs)
    
class RecipeDetail(DetailView):
    model = Recipe
    template_name = "imly_recipe_detail.html"
        
        