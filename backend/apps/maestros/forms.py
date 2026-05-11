from django import forms

from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro, SolicitudAsesoria


class RegistroMaestroPymeForm(forms.ModelForm):
    class Meta:
        model = PerfilMaestroPyme
        fields = [
            "tipo",
            "rut",
            "rubro",
            "oficio",
            "nombre_empresa",
            "telefono",
            "direccion",
        ]


class ServicioMaestroForm(forms.ModelForm):
    class Meta:
        model = ServicioMaestro
        fields = [
            "titulo",
            "descripcion",
            "rubro",
            "zona_atencion",
            "precio_referencial",
        ]


class SolicitudAsesoriaForm(forms.ModelForm):
    class Meta:
        model = SolicitudAsesoria
        fields = [
            "nombre_cliente",
            "email_cliente",
            "telefono_cliente",
            "direccion_o_comuna",
            "comentario",
        ]
