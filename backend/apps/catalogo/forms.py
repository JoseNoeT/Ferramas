from django import forms
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Producto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "slug", "activa"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la categoria es obligatorio.")
        return nombre

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        base_slug = slug or slugify(nombre)
        if not base_slug:
            raise forms.ValidationError("No fue posible generar un slug valido.")

        slug_final = base_slug
        index = 2
        queryset = Categoria.objects.filter(slug=slug_final)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        while queryset.exists():
            slug_final = f"{base_slug}-{index}"
            index += 1
            queryset = Categoria.objects.filter(slug=slug_final)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

        return slug_final


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "slug",
            "descripcion",
            "precio",
            "en_oferta",
            "precio_oferta",
            "fecha_inicio_oferta",
            "fecha_fin_oferta",
            "stock",
            "imagen",
            "activo",
            "categoria",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["categoria"].queryset = Categoria.objects.order_by("nombre")

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre del producto es obligatorio.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None or precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is None or stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

    def clean_categoria(self):
        categoria = self.cleaned_data.get("categoria")
        if categoria is None:
            raise forms.ValidationError("La categoria es obligatoria.")
        return categoria

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        base_slug = slug or slugify(nombre)
        if not base_slug:
            raise forms.ValidationError("No fue posible generar un slug valido.")

        slug_final = base_slug
        index = 2
        queryset = Producto.objects.filter(slug=slug_final)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        while queryset.exists():
            slug_final = f"{base_slug}-{index}"
            index += 1
            queryset = Producto.objects.filter(slug=slug_final)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

        return slug_final