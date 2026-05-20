from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Producto


class Command(BaseCommand):
    help = "Carga productos de prueba en oferta para validacion visual"

    CATEGORIAS = [
        "Herramientas",
        "Pinturas",
        "Materiales Electricos",
        "Construccion",
        "Seguridad",
    ]

    PRODUCTOS_OFERTA = [
        {
            "nombre": "Taladro inalambrico 20V",
            "descripcion": "Taladro percutor compacto con dos baterias y maleta.",
            "precio": Decimal("89990.00"),
            "precio_oferta": Decimal("74990.00"),
            "stock": 14,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/taladro-percutor-650w.png",
        },
        {
            "nombre": "Sierra caladora 650W",
            "descripcion": "Sierra para cortes curvos en madera y laminados.",
            "precio": Decimal("55990.00"),
            "precio_oferta": Decimal("46990.00"),
            "stock": 11,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/sierra-caladora-500w.png",
        },
        {
            "nombre": "Pintura latex interior 1 galon blanca",
            "descripcion": "Pintura lavable de alto rendimiento para muros interiores.",
            "precio": Decimal("22990.00"),
            "precio_oferta": Decimal("17990.00"),
            "stock": 28,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/pintura-latex-blanca.png",
        },
        {
            "nombre": "Esmalte sintetico negro 1 litro",
            "descripcion": "Esmalte para metal y madera con terminacion brillante.",
            "precio": Decimal("12990.00"),
            "precio_oferta": Decimal("9990.00"),
            "stock": 33,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/esmalte-sintetico-blanco.png",
        },
        {
            "nombre": "Cable electrico 2.5 mm 100 metros",
            "descripcion": "Rollo de cobre para instalaciones residenciales.",
            "precio": Decimal("48990.00"),
            "precio_oferta": Decimal("41990.00"),
            "stock": 16,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/cable-electrico-25mm.png",
        },
        {
            "nombre": "Disyuntor termomagnetico 32A",
            "descripcion": "Proteccion electrica para tablero de distribucion.",
            "precio": Decimal("14990.00"),
            "precio_oferta": Decimal("11990.00"),
            "stock": 25,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/automatico-10a.png",
        },
        {
            "nombre": "Cemento estructural 25 kg",
            "descripcion": "Cemento de alta resistencia para obras y reparaciones.",
            "precio": Decimal("6290.00"),
            "precio_oferta": Decimal("5290.00"),
            "stock": 120,
            "categoria": "Construccion",
            "imagen": "/static/img/productos/cemento-25kg.png",
        },
        {
            "nombre": "Malla electrosoldada 2x3 metros",
            "descripcion": "Malla para refuerzo de losas y sobrecimientos.",
            "precio": Decimal("19990.00"),
            "precio_oferta": Decimal("16990.00"),
            "stock": 22,
            "categoria": "Construccion",
            "imagen": "/static/img/productos/tornillos-acero.png",
        },
        {
            "nombre": "Casco de seguridad con ajuste",
            "descripcion": "Casco certificado para faenas de construccion.",
            "precio": Decimal("10990.00"),
            "precio_oferta": Decimal("8490.00"),
            "stock": 38,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/casco-seguridad.png",
        },
        {
            "nombre": "Guantes anticorte nivel 5",
            "descripcion": "Guantes de proteccion para trabajo con herramientas.",
            "precio": Decimal("6990.00"),
            "precio_oferta": Decimal("5490.00"),
            "stock": 60,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/guantes-seguridad.png",
        },
    ]

    def handle(self, *args, **options):
        ahora = timezone.now()
        inicio_oferta = ahora - timedelta(days=1)
        fin_oferta = ahora + timedelta(days=30)

        categorias = {}
        for nombre_categoria in self.CATEGORIAS:
            slug_categoria = slugify(nombre_categoria)
            categoria, _ = Categoria.objects.update_or_create(
                slug=slug_categoria,
                defaults={"nombre": nombre_categoria, "activa": True},
            )
            categorias[nombre_categoria] = categoria

        productos_creados = 0
        productos_actualizados = 0

        for data in self.PRODUCTOS_OFERTA:
            categoria = categorias[data["categoria"]]
            slug_producto = slugify(data["nombre"])
            _, created = Producto.objects.update_or_create(
                slug=slug_producto,
                defaults={
                    "nombre": data["nombre"],
                    "descripcion": data["descripcion"],
                    "precio": data["precio"],
                    "stock": data["stock"],
                    "imagen": data.get("imagen", "/static/img/productos/producto-default.png"),
                    "activo": True,
                    "categoria": categoria,
                    "en_oferta": True,
                    "precio_oferta": data["precio_oferta"],
                    "fecha_inicio_oferta": inicio_oferta,
                    "fecha_fin_oferta": fin_oferta,
                },
            )
            if created:
                productos_creados += 1
            else:
                productos_actualizados += 1

        total_ofertas_activas = Producto.objects.filter(
            activo=True,
            en_oferta=True,
            fecha_inicio_oferta__lte=ahora,
            fecha_fin_oferta__gte=ahora,
        ).count()

        self.stdout.write(self.style.SUCCESS("Carga de ofertas de prueba completada."))
        self.stdout.write(
            f"Productos en oferta -> creados: {productos_creados}, actualizados/reutilizados: {productos_actualizados}"
        )
        self.stdout.write(f"Productos en oferta activos: {total_ofertas_activas}")
