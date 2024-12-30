from django import template
from urllib.parse import urlencode, parse_qs, urlparse

register = template.Library()

@register.filter
def remove_query_param(querystring, param):
    """
    Belirtilen parametreyi querystring'den kaldırır.
    """
    query_dict = parse_qs(querystring)
    if param in query_dict:
        query_dict.pop(param)
    return urlencode(query_dict, doseq=True)
