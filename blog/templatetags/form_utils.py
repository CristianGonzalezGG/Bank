from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None

@register.filter
def get_field_errors(form, field_name):
    try:
        return form[field_name].errors
    except KeyError:
        return None

@register.filter
def concat(str1, str2):
    return str(str1) + str(str2) 