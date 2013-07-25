from imly.models import Recipe, Product, Ingredient
from imly.forms import RecipeForm, RecipeStepForm, RecipeStepFormSet, RecipeIngredientFormSet, RecipeIngredientFormSetEdit, RecipeStepFormSetEdit
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden,HttpResponseRedirect


class RecipeList(ListView):
    model = Recipe
    template_name = "imly_recipe_list.html"
    
    
class AddRecipe(CreateView):
    form_class = RecipeForm
    model = Recipe
    template_name = "imly_recipe_add.html"
    success_url = "/account/store/products/"
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        context = self.get_context_data()
        recipe_step_form = context['recipe_step_form']
        recipe_ingredient_form = context["recipe_ingredient_form"]
        recipe = form.save(commit=False)
        recipe.product = Product.objects.get(slug=self.kwargs["slug"],store=self.request.user.store)
        recipe.save()
        recipe_step_form.instance = recipe
        recipe_ingredient_form.instance = recipe
        if recipe_step_form.is_valid() and recipe_ingredient_form.is_valid():
            recipe_step_form.save()
            recipe_ingredient_form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)
        return super(AddRecipe, self).form_valid(form)
    

    def get_context_data(self, **kwargs):
        context = super(AddRecipe, self).get_context_data(**kwargs)
        context["product"] = Product.objects.get(slug=self.kwargs["slug"],store=self.request.user.store)
        if self.request.POST:
            context["recipe_step_form"] = RecipeStepFormSet(self.request.POST)
            context["recipe_ingredient_form"] = RecipeIngredientFormSet(self.request.POST)
        else:
            context["recipe_step_form"] = RecipeStepFormSet()
            context["recipe_ingredient_form"] = RecipeIngredientFormSet()
        return context
    
    
class EditRecipe(UpdateView):
    form_class = RecipeForm
    model = Recipe
    template_name = "imly_recipe_edit.html"
    success_url = "/account/store/products/"
        
    def get_object(self):
        return get_object_or_404(Recipe, product=Product.objects.get(slug=self.kwargs["slug"],store=self.request.user.store))
        
    def get(self, request, *args, **kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(EditRecipe,self).get(request,*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        super_return = super(EditRecipe, self).post(request, *args, **kwargs)
        recipe = self.get_object()
        recipe_step_formset = RecipeStepFormSetEdit(self.request.POST,instance=recipe)
        recipe_ingredient_formset = RecipeIngredientFormSetEdit(self.request.POST,instance=recipe)
        if recipe_step_formset.is_valid() and recipe_ingredient_formset.is_valid() :
            recipe_step_formset.save()
            recipe_ingredient_formset.save()
            return super_return
        
        else:
            return self.form_invalid()
        
    def get_context_data(self, **kwargs):
        context = super(EditRecipe, self).get_context_data(**kwargs)
        context["product"] = Product.objects.get(slug=self.kwargs["slug"],store=self.request.user.store)
        recipe = self.get_object()
        if self.request.POST:
            context["recipe_step_form"] = RecipeStepFormSetEdit(self.request.POST,queryset=recipe.steps.all(),instance=recipe)
            context["recipe_ingredient_form"] = RecipeIngredientFormSetEdit(self.request.POST,queryset=recipe.ingredients.all(),instance=recipe)
        else:
            context["recipe_step_form"] = RecipeStepFormSetEdit(queryset=recipe.steps.all(),instance=recipe)
            context["recipe_ingredient_form"] = RecipeIngredientFormSetEdit(queryset=recipe.ingredients.all(),instance=recipe)
        return context
    
class RecipeDetail(DetailView):
    model = Recipe
    template_name = "imly_recipe_detail.html"
        
        