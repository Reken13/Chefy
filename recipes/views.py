from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Recipe, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientFormSet


@login_required
def recipe_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')

    recipes = Recipe.objects.filter(is_active=True).prefetch_related('recipe_ingredients__ingredient')
    if q:
        recipes = recipes.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        recipes = recipes.filter(category=category)

    context = {
        'recipes': recipes,
        'categories': Recipe.Category.choices,
        'q': q,
        'selected_category': category,
    }
    return render(request, 'recipes/recipe_list.html', context)


@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    scale = float(request.GET.get('scale', 1))
    context = {
        'recipe': recipe,
        'scale': scale,
        'ingredients': recipe.recipe_ingredients.select_related('ingredient').all(),
        'steps': recipe.get_steps_list(),
    }
    return render(request, 'recipes/recipe_detail.html', context)


@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            formset.instance = recipe
            formset.save()
            messages.success(request, f'Receta "{recipe.name}" creada correctamente.')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()
    return render(request, 'recipes/recipe_form.html', {
        'form': form, 'formset': formset, 'title': 'Nueva Receta'
    })


@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Receta actualizada.')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {
        'form': form, 'formset': formset, 'recipe': recipe, 'title': 'Editar Receta'
    })
