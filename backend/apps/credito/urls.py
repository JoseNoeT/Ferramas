from django.urls import path

from apps.credito.views import saldo_cuenta_corriente_view, total_deuda_cuenta_corriente_view

urlpatterns = [
    path(
        "mi-cuenta/saldo-cuenta-corriente/",
        saldo_cuenta_corriente_view,
        name="api_credito_saldo_cuenta_corriente",
    ),
    path(
        "mi-cuenta/total-deuda/",
        total_deuda_cuenta_corriente_view,
        name="api_credito_total_deuda",
    ),
]
