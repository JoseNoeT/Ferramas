from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def formato_moneda(value):
    """Formatea montos enteros con separador de miles usando punto."""
    if value in (None, ""):
        return "0"

    try:
        monto = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    entero = int(monto)
    return f"{entero:,}".replace(",", ".")