from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()


def _car_body_svg(color):
    return f'''<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="100" cy="86" rx="82" ry="6" fill="#000" opacity="0.35"/>
<path d="M14,64 C14,50 28,44 42,42 L58,22 C64,15 75,11 90,11 L128,11 C142,11 152,15 160,23 L176,42 C188,44 198,50 198,62 L198,66 C198,71 193,74 185,74 L172,74 C172,60 161,51 148,51 C135,51 125,60 125,74 L78,74 C78,60 68,51 55,51 C42,51 32,60 32,74 L20,74 C13,74 14,69 14,64 Z" fill="{color}" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
<path d="M58,24 L68,26 C72,20 80,17 92,17 L124,17 C134,17 142,20 148,26 L158,24 L150,32 L64,32 Z" fill="#0d0e11" opacity="0.85"/>
<circle cx="55" cy="74" r="17" fill="#111"/><circle cx="55" cy="74" r="8" fill="#3a3b42"/><circle cx="55" cy="74" r="4" fill="#0a0a0c"/>
<circle cx="148" cy="74" r="17" fill="#111"/><circle cx="148" cy="74" r="8" fill="#3a3b42"/><circle cx="148" cy="74" r="4" fill="#0a0a0c"/>
<rect x="16" y="52" width="10" height="4" fill="#ffc629" opacity="0.9"/>
<rect x="178" y="52" width="10" height="4" fill="#e4002b" opacity="0.9"/>
</svg>'''


def _car_body_svg_classic(color):
    return f'''<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="100" cy="86" rx="82" ry="6" fill="#000" opacity="0.35"/>
<path d="M14,64 C14,50 28,44 42,42 L58,22 C64,15 75,11 90,11 L128,11 C142,11 152,15 160,23 L176,42 C188,44 198,50 198,62 L198,66 C198,71 193,74 185,74 L172,74 C172,60 161,51 148,51 C135,51 125,60 125,74 L78,74 C78,60 68,51 55,51 C42,51 32,60 32,74 L20,74 C13,74 14,69 14,64 Z" fill="{color}" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
<path d="M58,24 L68,26 C72,20 80,17 92,17 L124,17 C134,17 142,20 148,26 L158,24 L150,32 L64,32 Z" fill="#0d0e11" opacity="0.85"/>
<circle cx="55" cy="74" r="17" fill="#111"/><circle cx="55" cy="74" r="12" fill="#e8e8e8"/><circle cx="55" cy="74" r="4" fill="#0a0a0c"/>
<circle cx="148" cy="74" r="17" fill="#111"/><circle cx="148" cy="74" r="12" fill="#e8e8e8"/><circle cx="148" cy="74" r="4" fill="#0a0a0c"/>
<rect x="16" y="52" width="10" height="4" fill="#ffc629" opacity="0.9"/>
<rect x="178" y="52" width="10" height="4" fill="#e4002b" opacity="0.9"/>
</svg>'''


def _car_f1_svg(color):
    return f'''<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="100" cy="86" rx="86" ry="6" fill="#000" opacity="0.35"/>
<path d="M10 40 L34 40 L34 30 L10 30 Z" fill="{color}"/>
<path d="M166 40 L190 40 L190 30 L166 30 Z" fill="{color}"/>
<path d="M40,62 L36,74 L22,74 C15,74 12,70 12,64 C12,60 16,58 22,58 L40,58 Z" fill="{color}"/>
<path d="M160,62 L164,74 L178,74 C185,74 188,70 188,64 C188,60 184,58 178,58 L160,58 Z" fill="{color}"/>
<path d="M40,66 C40,60 46,56 60,55 L74,40 L126,40 L140,55 C154,56 160,60 160,66 L160,72 L128,72 L128,64 L72,64 L72,72 L40,72 Z" fill="{color}" stroke="rgba(255,255,255,0.15)"/>
<path d="M84,42 L88,52 L112,52 L116,42 Z" fill="#0d0e11"/>
<rect x="86" y="30" width="28" height="6" fill="{color}"/>
<circle cx="30" cy="76" r="16" fill="#111"/><circle cx="30" cy="76" r="7" fill="#3a3b42"/>
<circle cx="170" cy="76" r="16" fill="#111"/><circle cx="170" cy="76" r="7" fill="#3a3b42"/>
</svg>'''


@register.simple_tag
def car_svg(product, angle=0):
    """Render an inline SVG placeholder illustration for a product, themed by its accent color."""
    color = getattr(product, 'accent_color', '#e4002b') or '#e4002b'
    car_type = getattr(product, 'car_type', 'super')
    if car_type == 'f1':
        svg = _car_f1_svg(color)
    elif car_type == 'classic':
        svg = _car_body_svg_classic(color)
    else:
        svg = _car_body_svg(color)
    rotations = [0, -6, 6, 3]
    flip = -1 if angle == 2 else 1
    rot = rotations[angle % 4]
    wrapped = f'<div class="hw-car-art" style="transform:rotate({rot}deg) scaleX({flip});">{svg}</div>'
    return mark_safe(wrapped)


@register.filter
def mul(value, arg):
    try:
        return round(float(value) * float(arg), 2)
    except (TypeError, ValueError):
        return ''


@register.filter
def star_range(rating):
    try:
        r = int(round(float(rating)))
    except (TypeError, ValueError):
        r = 0
    return range(r)


@register.filter
def empty_star_range(rating):
    try:
        r = int(round(float(rating)))
    except (TypeError, ValueError):
        r = 0
    return range(5 - r)
