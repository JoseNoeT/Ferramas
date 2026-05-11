from django.urls import path

from apps.pagos import views

urlpatterns = [
    path("webpay/iniciar/", views.webpay_iniciar_view, name="api_webpay_iniciar"),
    path("webpay/retorno/", views.webpay_retorno_view, name="api_webpay_retorno"),
]
