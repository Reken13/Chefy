from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import User
from .forms import LoginForm, UserProfileForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        request.user.dark_mode = not request.user.dark_mode
        request.user.save(update_fields=['dark_mode'])
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def tutorial_view(request):
    sections = [
        {'key': 'inicio',      'label': 'Inicio',      'icon': 'home'},
        {'key': 'inventario',  'label': 'Inventario',  'icon': 'box'},
        {'key': 'mise',        'label': 'Mise en Place','icon': 'tasks'},
        {'key': 'recetas',     'label': 'Recetas',     'icon': 'book-open'},
        {'key': 'compras',     'label': 'Compras',     'icon': 'shopping-cart'},
        {'key': 'equipos',     'label': 'Equipos',     'icon': 'wrench'},
    ]
    quick_add_examples = [
        {'input': 'Tomate 5kg',    'result': '5 kg · Vegetales · Nevera'},
        {'input': 'Leche 3L',      'result': '3 L · Lácteos · Nevera'},
        {'input': 'Harina 10kg',   'result': '10 kg · Secos · Almacén'},
        {'input': 'Pollo 8kg',     'result': '8 kg · Carnes · Congelador'},
    ]
    import_formats = [
        {'label': 'Natural',  'example': 'Tomate 5kg\nLeche 3L\nPollo 8kg'},
        {'label': 'CSV',      'example': 'Tomate, 5, kg\nLeche, 3, L\nPollo, 8, kg'},
        {'label': 'Punto y coma', 'example': 'Tomate; 5; kg\nLeche; 3; L'},
    ]
    scales = [
        {'val': '0.5', 'label': 'Mitad',  'active': False},
        {'val': '1',   'label': 'Normal', 'active': True},
        {'val': '2',   'label': 'Doble',  'active': False},
        {'val': '3',   'label': 'Triple', 'active': False},
    ]
    return render(request, 'core/tutorial.html', {
        'sections': sections,
        'quick_add_examples': quick_add_examples,
        'import_formats': import_formats,
        'scales': scales,
    })


@login_required
def onboarding_view(request):
    from inventory.models import Ingredient, Category
    from inventory.kitchen_templates import KITCHEN_TEMPLATES, RESTAURANT_TYPES

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'skip':
            request.session['onboarding_done'] = True
            return redirect('dashboard')

        if action == 'complete':
            template_key = request.POST.get('template')
            restaurant_name = request.POST.get('restaurant_name', '').strip()

            if restaurant_name:
                request.user.restaurant_name = restaurant_name
                request.user.save(update_fields=['restaurant_name'])

            if template_key and template_key in KITCHEN_TEMPLATES:
                template = KITCHEN_TEMPLATES[template_key]
                cat_map = {}
                for cat_data in template.get('categories', []):
                    cat, _ = Category.objects.get_or_create(
                        name=cat_data['name'],
                        defaults={'color': cat_data['color'], 'icon': cat_data.get('icon', 'box')}
                    )
                    cat_map[cat_data['name']] = cat

                created = 0
                for ing_data in template.get('ingredients', []):
                    cat = cat_map.get(ing_data.get('category', ''))
                    _, was_created = Ingredient.objects.get_or_create(
                        name__iexact=ing_data['name'],
                        defaults={
                            'name': ing_data['name'],
                            'unit': ing_data['unit'],
                            'location': ing_data.get('location', 'almacen'),
                            'minimum_stock': ing_data.get('min_stock', 0),
                            'category': cat,
                        }
                    )
                    if was_created:
                        created += 1
                messages.success(request, f'¡Listo! Cargamos {created} ingredientes base para tu cocina.')

            request.session['onboarding_done'] = True
            return redirect('dashboard')

    # Build template previews
    import json
    template_previews_dict = {}
    for key, tpl in KITCHEN_TEMPLATES.items():
        template_previews_dict[key] = {
            'label': tpl['label'],
            'count': len(tpl['ingredients']),
            'sample': [i['name'] for i in tpl['ingredients'][:4]],
        }

    restaurant_types = [
        {'key': key, 'label': label, 'icon': icon}
        for key, label, icon in RESTAURANT_TYPES
    ]

    return render(request, 'core/onboarding.html', {
        'restaurant_types': restaurant_types,
        'template_previews': template_previews_dict,
        'template_previews_json': json.dumps(template_previews_dict),
    })
