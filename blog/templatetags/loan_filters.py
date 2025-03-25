from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def subtract(value, arg):
    """Resta arg de value"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        return value 