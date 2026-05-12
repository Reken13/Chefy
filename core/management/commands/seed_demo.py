from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random


class Command(BaseCommand):
    help = 'Seeds the database with demo data for Chefy'

    def handle(self, *args, **kwargs):
        self.stdout.write('🍴 Creando datos de demostración para Chefy...')
        self._create_users()
        self._create_categories()
        self._create_ingredients()
        self._create_recipes()
        self._create_mise_en_place()
        self._create_equipment_issues()
        self._create_waste_logs()
        self._create_production_tasks()
        self.stdout.write(self.style.SUCCESS('✅ Demo data creado exitosamente!'))
        self.stdout.write('👤 Usuario: admin / admin123')
        self.stdout.write('👤 Chef ejecutivo: chef / chef123')
        self.stdout.write('👤 Cocinero: cook / cook123')

    def _create_users(self):
        from core.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@chefy.app', 'admin123',
                first_name='Admin', last_name='Chefy',
                restaurant_name='Restaurante Demo', role='executive_chef')

        if not User.objects.filter(username='chef').exists():
            User.objects.create_user('chef', 'chef@chefy.app', 'chef123',
                first_name='Carlos', last_name='Mendoza',
                role='executive_chef', restaurant_name='Restaurante Demo')

        if not User.objects.filter(username='sous').exists():
            User.objects.create_user('sous', 'sous@chefy.app', 'sous123',
                first_name='Ana', last_name='García',
                role='sous_chef', restaurant_name='Restaurante Demo')

        if not User.objects.filter(username='cook').exists():
            User.objects.create_user('cook', 'cook@chefy.app', 'cook123',
                first_name='Luis', last_name='Torres',
                role='cook', restaurant_name='Restaurante Demo')
        self.stdout.write('  ✓ Usuarios creados')

    def _create_categories(self):
        from inventory.models import Category
        categories = [
            ('Carnes', '#ef4444', 'drumstick-bite'),
            ('Vegetales', '#22c55e', 'leaf'),
            ('Lácteos', '#f59e0b', 'cheese'),
            ('Granos y Cereales', '#8b5cf6', 'wheat'),
            ('Hierbas y Especias', '#10b981', 'seedling'),
            ('Aceites y Grasas', '#f97316', 'droplet'),
            ('Mariscos', '#3b82f6', 'fish'),
            ('Frutas', '#ec4899', 'apple-alt'),
            ('Bebidas y Licores', '#6366f1', 'wine-bottle'),
            ('Panadería', '#d97706', 'bread-slice'),
        ]
        for name, color, icon in categories:
            Category.objects.get_or_create(name=name, defaults={'color': color, 'icon': icon})
        self.stdout.write('  ✓ Categorías creadas')

    def _create_ingredients(self):
        from inventory.models import Ingredient, Category
        today = date.today()

        ingredients_data = [
            ('Lomo de res', 'Carnes', 'kg', 8.5, 5.0, 45000, None, 'freezer', 'Frigorífico Central'),
            ('Pechuga de pollo', 'Carnes', 'kg', 3.2, 4.0, 12000, today + timedelta(days=2), 'nevera', 'Distribuidora Aves'),
            ('Lomo de cerdo', 'Carnes', 'kg', 12.0, 6.0, 18000, None, 'freezer', 'Frigorífico Central'),
            ('Camarones tigre', 'Mariscos', 'kg', 1.5, 3.0, 55000, today + timedelta(days=1), 'freezer', 'Mariscos del Pacífico'),
            ('Leche entera', 'Lácteos', 'l', 4.0, 5.0, 3200, today + timedelta(days=3), 'nevera', 'Lácteos Andinos'),
            ('Mantequilla', 'Lácteos', 'kg', 2.5, 2.0, 18000, today + timedelta(days=15), 'nevera', 'Lácteos Andinos'),
            ('Crema de leche', 'Lácteos', 'l', 3.0, 3.0, 8500, today + timedelta(days=7), 'nevera', 'Lácteos Andinos'),
            ('Queso parmesano', 'Lácteos', 'kg', 1.2, 1.0, 45000, today + timedelta(days=30), 'nevera', 'Importadora Gourmet'),
            ('Tomate chonto', 'Vegetales', 'kg', 8.0, 5.0, 2500, today + timedelta(days=5), 'nevera', 'Finca Orgánica'),
            ('Cebolla cabezona', 'Vegetales', 'kg', 6.5, 4.0, 1800, None, 'almacen', 'Finca Orgánica'),
            ('Ajo', 'Vegetales', 'kg', 2.3, 2.0, 12000, None, 'almacen', 'Finca Orgánica'),
            ('Pimentón rojo', 'Vegetales', 'kg', 4.0, 3.0, 4500, today + timedelta(days=8), 'nevera', 'Finca Orgánica'),
            ('Harina de trigo', 'Granos y Cereales', 'kg', 18.0, 10.0, 2200, None, 'almacen', 'Molinos del Valle'),
            ('Arroz blanco', 'Granos y Cereales', 'kg', 25.0, 15.0, 2800, None, 'almacen', 'Arrocera Nacional'),
            ('Lentejas', 'Granos y Cereales', 'kg', 5.0, 3.0, 4500, None, 'almacen', 'Granos y Legumbres'),
            ('Aceite de oliva', 'Aceites y Grasas', 'l', 2.5, 2.0, 28000, None, 'almacen', 'Importadora Gourmet'),
            ('Aceite vegetal', 'Aceites y Grasas', 'l', 8.0, 5.0, 7500, None, 'almacen', 'Distribuidora Nacional'),
            ('Tomillo fresco', 'Hierbas y Especias', 'g', 150, 100, 80, today + timedelta(days=4), 'nevera', 'Hierbas Frescas'),
            ('Romero', 'Hierbas y Especias', 'g', 80, 100, 90, today + timedelta(days=4), 'nevera', 'Hierbas Frescas'),
            ('Pimienta negra molida', 'Hierbas y Especias', 'g', 500, 200, 35, None, 'almacen', 'Especias del Mundo'),
            ('Sal marina', 'Hierbas y Especias', 'kg', 3.0, 2.0, 1500, None, 'almacen', 'Salinas Nacionales'),
            ('Huevos', 'Lácteos', 'und', 48, 30, 600, today + timedelta(days=10), 'nevera', 'Avícola del Valle'),
            ('Mango', 'Frutas', 'kg', 5.5, 3.0, 3500, today + timedelta(days=5), 'almacen', 'Frutas Tropicales'),
            ('Limón tahití', 'Frutas', 'und', 25, 20, 500, today + timedelta(days=7), 'almacen', 'Frutas Tropicales'),
            ('Vino blanco', 'Bebidas y Licores', 'l', 2.0, 1.0, 35000, None, 'bar', 'Licores y Vinos'),
            ('Pan baguette', 'Panadería', 'und', 8, 5, 4500, today + timedelta(days=1), 'almacen', 'Panadería Artesanal'),
        ]

        categories_map = {c.name: c for c in Category.objects.all()}

        for name, cat_name, unit, stock, min_stock, cost, expiry, location, supplier in ingredients_data:
            Ingredient.objects.get_or_create(
                name=name,
                defaults={
                    'category': categories_map.get(cat_name),
                    'unit': unit,
                    'current_stock': stock,
                    'minimum_stock': min_stock,
                    'cost_per_unit': cost,
                    'expiry_date': expiry,
                    'location': location,
                    'supplier': supplier,
                }
            )
        self.stdout.write('  ✓ Ingredientes creados')

    def _create_recipes(self):
        from recipes.models import Recipe, RecipeIngredient
        from inventory.models import Ingredient
        from core.models import User

        chef = User.objects.filter(role='executive_chef').first()

        def get_ing(name):
            return Ingredient.objects.filter(name=name).first()

        recipes_data = [
            {
                'name': 'Lomo al Vino Tinto',
                'category': 'principal',
                'description': 'Lomo de res sellado y braseado en vino tinto con hierbas aromáticas',
                'yield_quantity': 4,
                'yield_unit': 'porciones',
                'prep_time': 20,
                'cook_time': 45,
                'sale_price': 65000,
                'steps': 'Sellar el lomo en aceite bien caliente por todos los lados\nAgregar ajo y cebolla picados finos\nDesglasar con vino tinto\nAgregar tomillo y romero\nBrasear en horno a 180°C por 35 minutos\nReposar 10 minutos antes de servir',
                'ingredients': [
                    ('Lomo de res', 0.8),
                    ('Vino blanco', 0.25),
                    ('Cebolla cabezona', 0.15),
                    ('Ajo', 0.02),
                    ('Tomillo fresco', 10),
                    ('Romero', 8),
                    ('Aceite de oliva', 0.03),
                    ('Sal marina', 0.005),
                    ('Pimienta negra molida', 0.003),
                ]
            },
            {
                'name': 'Risotto de Mariscos',
                'category': 'principal',
                'description': 'Risotto cremoso con camarones tigre y queso parmesano',
                'yield_quantity': 4,
                'yield_unit': 'porciones',
                'prep_time': 15,
                'cook_time': 35,
                'sale_price': 55000,
                'steps': 'Saltear cebolla en mantequilla hasta transparente\nAgregar arroz y tostar 2 minutos\nAgregar vino blanco y dejar evaporar\nIncorporar caldo caliente de a poco, revolviendo constantemente\nEn los últimos 5 minutos agregar camarones salteados\nTerminar con mantequilla fría y parmesano',
                'ingredients': [
                    ('Camarones tigre', 0.4),
                    ('Arroz blanco', 0.3),
                    ('Cebolla cabezona', 0.1),
                    ('Vino blanco', 0.1),
                    ('Mantequilla', 0.06),
                    ('Queso parmesano', 0.08),
                    ('Sal marina', 0.003),
                    ('Pimienta negra molida', 0.002),
                ]
            },
            {
                'name': 'Pollo a las Hierbas',
                'category': 'principal',
                'description': 'Pechuga de pollo marinada en hierbas frescas y asada al horno',
                'yield_quantity': 4,
                'yield_unit': 'porciones',
                'prep_time': 30,
                'cook_time': 25,
                'sale_price': 42000,
                'steps': 'Marinar pollo con aceite oliva, ajo, tomillo y romero por 2 horas\nSazonar con sal y pimienta\nSellar en sartén caliente 2 minutos por lado\nTerminar en horno a 200°C por 15 minutos\nReposar 5 minutos',
                'ingredients': [
                    ('Pechuga de pollo', 0.8),
                    ('Aceite de oliva', 0.04),
                    ('Ajo', 0.015),
                    ('Tomillo fresco', 15),
                    ('Romero', 10),
                    ('Sal marina', 0.005),
                    ('Pimienta negra molida', 0.003),
                    ('Limón tahití', 2),
                ]
            },
            {
                'name': 'Ceviche de Camarones',
                'category': 'entrada',
                'description': 'Camarones marinados en limón con tomate y cilantro',
                'yield_quantity': 6,
                'yield_unit': 'porciones',
                'prep_time': 20,
                'cook_time': 0,
                'sale_price': 38000,
                'steps': 'Limpiar y cortar camarones en trozos medianos\nMarinar en jugo de limón por 20 minutos\nAgregar tomate, cebolla, pimentón picados en brunoise\nSazonar con sal y pimienta\nServir frío',
                'ingredients': [
                    ('Camarones tigre', 0.5),
                    ('Limón tahití', 8),
                    ('Tomate chonto', 0.2),
                    ('Cebolla cabezona', 0.1),
                    ('Pimentón rojo', 0.1),
                    ('Sal marina', 0.003),
                    ('Pimienta negra molida', 0.002),
                ]
            },
            {
                'name': 'Crema de Tomate',
                'category': 'entrada',
                'description': 'Sopa cremosa de tomate con albahaca y crema de leche',
                'yield_quantity': 6,
                'yield_unit': 'porciones',
                'prep_time': 10,
                'cook_time': 30,
                'sale_price': 22000,
                'steps': 'Asar tomates en horno con ajo y cebolla\nLicuar con caldo de verduras\nColar y cocinar a fuego medio 15 minutos\nAgregar crema de leche\nSazonar y servir',
                'ingredients': [
                    ('Tomate chonto', 1.0),
                    ('Cebolla cabezona', 0.15),
                    ('Ajo', 0.02),
                    ('Crema de leche', 0.2),
                    ('Aceite de oliva', 0.03),
                    ('Sal marina', 0.005),
                    ('Pimienta negra molida', 0.002),
                ]
            },
            {
                'name': 'Salsa Demi-Glace',
                'category': 'salsa',
                'description': 'Salsa base reducida de fondo de res, ideal para acompañar carnes',
                'yield_quantity': 500,
                'yield_unit': 'ml',
                'prep_time': 10,
                'cook_time': 120,
                'sale_price': 0,
                'steps': 'Reducir fondo de res a la mitad\nAgregar vino tinto y reducir nuevamente\nMontar con mantequilla fría al final',
                'ingredients': [
                    ('Vino blanco', 0.5),
                    ('Mantequilla', 0.05),
                    ('Cebolla cabezona', 0.1),
                    ('Ajo', 0.01),
                    ('Tomillo fresco', 5),
                ]
            },
        ]

        for rdata in recipes_data:
            ingredients_list = rdata.pop('ingredients')
            recipe, created = Recipe.objects.get_or_create(
                name=rdata['name'],
                defaults={**rdata, 'created_by': chef}
            )
            if created:
                for ing_name, qty in ingredients_list:
                    ing = get_ing(ing_name)
                    if ing:
                        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=qty)
        self.stdout.write('  ✓ Recetas creadas')

    def _create_mise_en_place(self):
        from mise_en_place.models import MiseEnPlaceTask
        from core.models import User
        from recipes.models import Recipe

        today = timezone.now().date()
        sous = User.objects.filter(username='sous').first()
        cook = User.objects.filter(username='cook').first()
        chef = User.objects.filter(role='executive_chef').first()

        tasks = [
            ('Brunoise de verduras para ceviche', 'pendiente', 'alta', cook, 8, 30, '5 kg total'),
            ('Fondo de res — reducción demi-glace', 'en_proceso', 'critica', sous, 7, 0, '3 litros'),
            ('Marinar pollos para servicio noche', 'pendiente', 'media', cook, 12, 0, '8 piezas'),
            ('Mise en place para risotto — sofrito base', 'pendiente', 'alta', cook, 9, 0, '4 porciones'),
            ('Camarones limpios y desvenados', 'terminado', 'alta', sous, 7, 30, '2 kg'),
            ('Crema de tomate — preparación previa', 'terminado', 'media', cook, 8, 0, '6 porciones'),
            ('Pan baguette — rebanar y organizar', 'pendiente', 'baja', cook, 11, 0, '8 unidades'),
        ]

        now = timezone.now()
        for title, status, priority, assigned, hour, minute, quantity in tasks:
            deadline = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            MiseEnPlaceTask.objects.get_or_create(
                title=title,
                date=today,
                defaults={
                    'status': status,
                    'priority': priority,
                    'assigned_to': assigned,
                    'created_by': chef,
                    'deadline': deadline,
                    'quantity': quantity,
                }
            )
        self.stdout.write('  ✓ Mise en place creado')

    def _create_equipment_issues(self):
        from equipment.models import EquipmentIssue, Equipment
        from core.models import User

        cook = User.objects.filter(username='cook').first()
        sous = User.objects.filter(username='sous').first()

        issues = [
            ('Salamandra Grill', 'No calienta de manera uniforme, quema en el lado derecho', 'alta', 'en_reparacion', 'Área caliente', sous),
            ('Batidora planetaria Kitchen Aid', 'Hace ruido extraño al mezclar, posible falla en engranaje', 'media', 'pendiente', 'Pastelería', cook),
            ('Horno convector #2', 'Puerta no sella correctamente, pierde temperatura', 'critica', 'pendiente', 'Cocina principal', sous),
            ('Refrigerador walk-in', 'Temperatura subió a 8°C esta mañana, revisar compresor', 'critica', 'en_reparacion', 'Área fría', sous),
        ]

        for eq_name, desc, priority, status, location, reported in issues:
            EquipmentIssue.objects.get_or_create(
                equipment_name=eq_name,
                equipment=None,
                defaults={
                    'description': desc,
                    'priority': priority,
                    'status': status,
                    'location': location,
                    'reported_by': reported,
                }
            )
        self.stdout.write('  ✓ Problemas de equipo creados')

    def _create_waste_logs(self):
        from waste.models import WasteLog
        from inventory.models import Ingredient
        from core.models import User

        cook = User.objects.filter(username='cook').first()
        today = date.today()

        wastes = [
            ('Pechuga de pollo', 0.3, 'dañado', 'Se encontró manchado al abrir el empaque'),
            ('Tomate chonto', 0.5, 'vencido', 'Tomates del fondo de la caja en mal estado'),
            ('Crema de leche', 0.1, 'derrame', 'Accidente al sacar del refrigerador'),
            ('Tomillo fresco', 20, 'vencido', 'Estaba amarillo y sin olor'),
        ]

        for ing_name, qty, reason, desc in wastes:
            ing = Ingredient.objects.filter(name=ing_name).first()
            if ing:
                WasteLog.objects.get_or_create(
                    ingredient=ing,
                    date=today,
                    reason=reason,
                    defaults={
                        'quantity': qty,
                        'description': desc,
                        'reported_by': cook,
                        'cost': qty * float(ing.cost_per_unit),
                    }
                )
        self.stdout.write('  ✓ Desperdicios registrados')

    def _create_production_tasks(self):
        from production.models import ProductionTask
        from recipes.models import Recipe
        from core.models import User

        cook = User.objects.filter(username='cook').first()
        sous = User.objects.filter(username='sous').first()
        chef = User.objects.filter(role='executive_chef').first()
        today = timezone.now().date()

        productions = [
            ('Lomo al Vino Tinto', 8, 'porciones', sous, 60),
            ('Risotto de Mariscos', 12, 'porciones', cook, 45),
            ('Pollo a las Hierbas', 10, 'porciones', cook, 30),
            ('Crema de Tomate', 15, 'porciones', sous, 40),
            ('Salsa Demi-Glace', 2000, 'ml', sous, 120),
        ]

        for recipe_name, qty, unit, assigned, est_time in productions:
            recipe = Recipe.objects.filter(name=recipe_name).first()
            if recipe:
                ProductionTask.objects.get_or_create(
                    recipe=recipe,
                    scheduled_date=today,
                    defaults={
                        'quantity': qty,
                        'unit': unit,
                        'assigned_to': assigned,
                        'created_by': chef,
                        'estimated_time': est_time,
                        'deduct_inventory': False,
                    }
                )
        self.stdout.write('  ✓ Producción del día creada')
