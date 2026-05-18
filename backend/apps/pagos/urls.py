from django.urls import path

from apps.pagos import views

app_name = "pagos"

urlpatterns = [
    path("webpay/iniciar/<int:pedido_id>/", views.iniciar_webpay_view, name="webpay_iniciar"),
    path("webpay/retorno/", views.retorno_webpay_view, name="webpay_retorno"),
]
