from django import template
from django.utils.text import Truncator

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return ''
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return '' 


@register.filter
def truncatewords_var(value, arg):
    try:
        length = int(arg)
    except ValueError:
        return value
    return Truncator(value).words(length, truncate='...')