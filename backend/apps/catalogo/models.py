from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    slug   = models.SlugField(unique=True, verbose_name="Slug")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name        = "Categoria"
        verbose_name_plural = "Categorias"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre      = models.CharField(max_length=150, verbose_name="Nombre")
    slug        = models.SlugField(unique=True, verbose_name="Slug")
    descripcion = models.TextField(verbose_name="Descripcion")
    precio      = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock       = models.PositiveIntegerField(default=0, verbose_name="Stock")
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name="Stock mínimo")
    imagen      = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Imagen (URL o ruta)"
    )
    activo      = models.BooleanField(default=True, verbose_name="Activo")
    en_oferta   = models.BooleanField(default=False, verbose_name="En oferta")
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio oferta",
    )
    fecha_inicio_oferta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio oferta",
    )
    fecha_fin_oferta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin oferta",
    )
    categoria   = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name ="productos",
        verbose_name ="Categoria",
    )
    fecha_creacion   = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")

    class Meta:
        verbose_name        = "Producto"
        verbose_name_plural = "Productos"
        ordering            = ["-fecha_creacion"]

    def __str__(self):
        return self.nombre
