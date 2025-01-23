from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='replace_underscores')
def replace_underscores(value):
    return value.replace('_', ' ')
