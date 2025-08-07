from django import template

register = template.Library()

@register.filter
def replace_gt_with_symbol(value):
    """ Belirli operatörleri matematiksel sembollerle değiştirir. """
    if value:
        replacements = {
            "GT": ">",
            "LT": "<",
            "GTE": ">=",
            "LTE": "<=",
            "EQ": "==",
            "NEQ": "!="
        }
        for key, symbol in replacements.items():
            value = value.replace(key, symbol)
    return value

