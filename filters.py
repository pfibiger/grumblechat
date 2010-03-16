from google.appengine.ext.webapp import template

register = template.create_template_register() 

@register.filter
def get(d, key_name):
    try:
        value = d.get(key_name)
    except KeyError:
        from django.conf import settings
        value = settings.TEMPLATE_STRING_IF_INVALID
    return value
