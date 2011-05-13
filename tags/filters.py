from google.appengine.ext.webapp import template
from django.template import Node

register = template.create_template_register() 

####
@register.filter
def get(d, key_name):
    try:
        value = d.get(key_name)
    except KeyError:
        from django.conf import settings
        value = settings.TEMPLATE_STRING_IF_INVALID
    return value

####
# 'assign' from http://www.djangosnippets.org/snippets/539/
class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''

@register.tag
def assign(parser, token):
    """
    Assign an expression to a variable in the current context.
    
    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}
        
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)
