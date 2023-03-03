# templates/filters/custom_filters.py

from django import template

register = template.Library()

@register.filter
def multiplicar(valor, multiplicador):
    return valor * multiplicador
