# templates/filters/custom_filters.py

from django import template

register = template.Library()

@register.filter
def multiplicar(valor, multiplicador):
    return valor * multiplicador

@register.filter
def divisor(valor, divisor):
    return int(valor / divisor)
