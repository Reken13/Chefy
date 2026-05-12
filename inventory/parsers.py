"""
Natural language parser for quick ingredient entry.
Supports: "Tomate 5kg", "Leche 3 litros", "Pollo 10 kg", "Huevos 24 und"
"""
import re
from decimal import Decimal

UNIT_MAP = {
    # Weight
    'kg': 'kg', 'kilo': 'kg', 'kilos': 'kg', 'kilogramo': 'kg', 'kilogramos': 'kg',
    'g': 'g', 'gr': 'g', 'gramo': 'g', 'gramos': 'g',
    # Volume
    'l': 'l', 'lt': 'l', 'lts': 'l', 'litro': 'l', 'litros': 'l',
    'ml': 'ml', 'mililitro': 'ml', 'mililitros': 'ml', 'cc': 'ml',
    # Count
    'und': 'und', 'unidad': 'und', 'unidades': 'und', 'u': 'und',
    'pza': 'und', 'pieza': 'und', 'piezas': 'und',
    'un': 'und', 'uni': 'und',
    # Containers
    'caja': 'caja', 'cajas': 'caja',
    # Portions
    'por': 'por', 'porcion': 'por', 'porciones': 'por', 'porción': 'por',
}

CATEGORY_KEYWORDS = {
    'Carnes': [
        'carne', 'res', 'pollo', 'cerdo', 'cordero', 'pato', 'pavo',
        'chorizo', 'tocino', 'jamón', 'jamon', 'salchicha', 'lomo',
        'costilla', 'filete', 'chuleta', 'ternera',
    ],
    'Mariscos': [
        'camarón', 'camaron', 'pescado', 'langosta', 'pulpo', 'calamar',
        'tilapia', 'salmón', 'salmon', 'atún', 'atun', 'trucha', 'bagre',
        'langostino', 'mejillón', 'mejillon', 'cangrejo',
    ],
    'Lácteos': [
        'leche', 'queso', 'mantequilla', 'crema', 'yogurt', 'nata',
        'mozzarella', 'parmesano', 'cheddar', 'requesón', 'manteca',
    ],
    'Vegetales': [
        'tomate', 'cebolla', 'ajo', 'papa', 'zanahoria', 'lechuga',
        'espinaca', 'pimentón', 'pimiento', 'brócoli', 'coliflor',
        'berenjena', 'zucchini', 'calabaza', 'apio', 'pepino',
        'remolacha', 'maíz', 'arveja', 'habichuela', 'frijol verde',
    ],
    'Frutas': [
        'manzana', 'naranja', 'limón', 'fresa', 'mango', 'pera',
        'banano', 'piña', 'uva', 'sandía', 'melón', 'papaya',
        'aguacate', 'maracuyá', 'guayaba', 'mora',
    ],
    'Granos y Legumbres': [
        'arroz', 'frijol', 'lenteja', 'garbanzo', 'maíz', 'trigo',
        'quinua', 'avena', 'cebada', 'soya',
    ],
    'Harinas y Pastas': [
        'harina', 'pasta', 'fideos', 'macarrón', 'espagueti', 'pan',
        'pan rallado', 'almidón', 'fécula', 'polenta',
    ],
    'Aceites y Salsas': [
        'aceite', 'vinagre', 'salsa', 'mayonesa', 'mostaza', 'ketchup',
        'soya', 'worcestershire', 'tabasco',
    ],
    'Especias y Hierbas': [
        'sal', 'pimienta', 'comino', 'canela', 'orégano', 'tomillo',
        'laurel', 'curry', 'páprika', 'paprika', 'cúrcuma', 'curcuma',
        'azafrán', 'cilantro', 'perejil', 'albahaca', 'romero',
    ],
    'Bebidas': [
        'agua', 'jugo', 'vino', 'cerveza', 'refresco', 'café', 'cafe',
        'té', 'te', 'leche de coco', 'crema de leche',
    ],
    'Azúcares y Dulces': [
        'azúcar', 'azucar', 'miel', 'panela', 'chocolate', 'cacao',
        'vainilla', 'mermelada', 'almíbar',
    ],
}

LOCATION_HINTS = {
    'nevera': ['leche', 'queso', 'huevo', 'mantequilla', 'crema', 'yogurt', 'tomate', 'lechuga', 'zanahoria', 'limón'],
    'freezer': ['carne', 'pollo', 'cerdo', 'pescado', 'camarón', 'mariscos', 'helado'],
    'bar': ['vino', 'cerveza', 'jugo', 'agua', 'refresco', 'café'],
}


def parse_quick_add(text: str) -> dict:
    """Parse a natural language ingredient entry into structured data."""
    text = text.strip()
    if not text:
        return {'valid': False, 'error': 'Entrada vacía'}

    # Pattern: name [qty] [unit]  or  [qty] [unit] name
    # Try: name followed by number+unit
    pattern = r'^(.+?)\s+(\d+(?:[.,]\d+)?)\s*([a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?$'
    match = re.match(pattern, text, re.IGNORECASE)
    if match:
        name = match.group(1).strip().title()
        qty_str = match.group(2).replace(',', '.')
        qty = Decimal(qty_str)
        unit_raw = (match.group(3) or '').lower().strip()
        unit = UNIT_MAP.get(unit_raw, 'und')
        return {
            'valid': True,
            'name': name,
            'quantity': qty,
            'unit': unit,
            'suggested_category': _detect_category(name),
            'suggested_location': _detect_location(name),
        }

    # Try: number+unit name (e.g. "5kg Tomate")
    pattern2 = r'^(\d+(?:[.,]\d+)?)\s*([a-zA-ZáéíóúÁÉÍÓÚñÑ]+)\s+(.+)$'
    match2 = re.match(pattern2, text, re.IGNORECASE)
    if match2:
        qty = Decimal(match2.group(1).replace(',', '.'))
        unit_raw = match2.group(2).lower().strip()
        unit = UNIT_MAP.get(unit_raw, 'und')
        name = match2.group(3).strip().title()
        return {
            'valid': True,
            'name': name,
            'quantity': qty,
            'unit': unit,
            'suggested_category': _detect_category(name),
            'suggested_location': _detect_location(name),
        }

    # Fallback: just a name, no quantity
    name = text.title()
    return {
        'valid': True,
        'name': name,
        'quantity': Decimal('0'),
        'unit': 'und',
        'suggested_category': _detect_category(name),
        'suggested_location': _detect_location(name),
    }


def parse_bulk_text(text: str) -> list:
    """Parse multiple lines of ingredient entries."""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Support comma/semicolon separated: name,qty,unit
        if ',' in line or ';' in line:
            parts = re.split(r'[,;]', line)
            if len(parts) >= 2:
                name = parts[0].strip().title()
                qty_str = parts[1].strip().replace(',', '.')
                try:
                    qty = Decimal(qty_str)
                except Exception:
                    qty = Decimal('0')
                unit = UNIT_MAP.get(parts[2].strip().lower() if len(parts) > 2 else '', 'und')
                results.append({
                    'valid': True,
                    'name': name,
                    'quantity': qty,
                    'unit': unit,
                    'suggested_category': _detect_category(name),
                    'suggested_location': _detect_location(name),
                    'raw': line,
                })
                continue
        result = parse_quick_add(line)
        result['raw'] = line
        results.append(result)
    return results


def _detect_category(name: str) -> str:
    name_lower = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return ''


def _detect_location(name: str) -> str:
    name_lower = name.lower()
    for location, keywords in LOCATION_HINTS.items():
        for kw in keywords:
            if kw in name_lower:
                return location
    return 'almacen'
