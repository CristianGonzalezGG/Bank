from django import template

register = template.Library()

@register.filter
def get_field(form, field_base):
    """Obtiene un campo del formulario basado en un nombre base y un índice"""
    return form[field_base]

@register.filter
def get_field_errors(form, field_base):
    """Obtiene los errores de un campo del formulario"""
    return form[field_base].errors 