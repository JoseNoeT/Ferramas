from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Producto


class Command(BaseCommand):
    help = "Carga categorias y productos de prueba para el catalogo REST"

    CATEGORIAS = [
        "Herramientas",
        "Pinturas",
        "Materiales Electricos",
        "Seguridad",
        "Construccion",
    ]

    PRODUCTOS_POR_CATEGORIA = {
        "Herramientas": [
            ("Taladro percutor 650W", "Taladro compacto para trabajos domesticos.", Decimal("59990"), 18),
            ("Juego de llaves mixtas 12 piezas", "Set de acero cromo vanadio.", Decimal("24990"), 30),
            ("Sierra circular 7 1/4", "Corte preciso para madera y tableros.", Decimal("79990"), 12),
            ("Martillo carpintero 16oz", "Mango ergonomico antideslizante.", Decimal("8990"), 40),
            ("Alicate universal 8", "Alicate reforzado para uso general.", Decimal("6990"), 35),
        ],
        "Pinturas": [
            ("Esmalte al agua blanco 1 galon", "Acabado lavable para interiores.", Decimal("19990"), 22),
            ("Latex exterior beige 1 galon", "Proteccion UV para fachadas.", Decimal("21990"), 15),
            ("Spray anticorrosivo negro mate", "Cobertura rapida para metal.", Decimal("6490"), 50),
            ("Barniz marino brillante 1 litro", "Proteccion para maderas expuestas.", Decimal("12990"), 20),
            ("Rodillo microfibra 9 pulgadas", "Aplicacion uniforme en muros.", Decimal("3990"), 60),
        ],
        "Materiales Electricos": [
            ("Cable electrico THHN 2.5mm 100m", "Conductor de cobre para instalaciones domiciliarias.", Decimal("45990"), 10),
            ("Interruptor simple embutido", "Mecanismo modular de pared.", Decimal("2490"), 80),
            ("Enchufe doble 10A", "Placa doble para uso residencial.", Decimal("2990"), 70),
            ("Disyuntor 25A riel DIN", "Proteccion contra sobrecorriente.", Decimal("10990"), 25),
            ("Ampolleta LED E27 12W luz fria", "Bajo consumo y larga vida util.", Decimal("1990"), 120),
        ],
        "Seguridad": [
            ("Guantes de seguridad nitrilo", "Proteccion de manos para trabajo pesado.", Decimal("3490"), 90),
            ("Casco de seguridad amarillo", "Casco certificado para obra.", Decimal("8990"), 45),
            ("Lentes de proteccion transparentes", "Proteccion ocular anti-impacto.", Decimal("2990"), 65),
            ("Botin de seguridad punta de acero", "Calzado de seguridad dielctrico.", Decimal("35990"), 28),
            ("Arnes de seguridad cuerpo completo", "Arnes con anillo dorsal para altura.", Decimal("58990"), 14),
        ],
        "Construccion": [
            ("Cemento alta resistencia 25kg", "Bolsa para obras y reparaciones.", Decimal("5490"), 120),
            ("Arena fina saco 25kg", "Arena seleccionada para terminaciones.", Decimal("2990"), 100),
            ("Ladrillo fiscal unidad", "Ladrillo tradicional para muros.", Decimal("490"), 1000),
            ("Malla electrosoldada 2x3m", "Refuerzo estructural para losas.", Decimal("18990"), 35),
            ("Yeso en polvo 20kg", "Yeso para enlucidos interiores.", Decimal("6990"), 55),
        ],
    }

    def handle(self, *args, **options):
        categorias_activas = []
        categorias_creadas = 0
        categorias_actualizadas = 0
        productos_creados = 0
        productos_actualizados = 0

        for nombre_categoria in self.CATEGORIAS:
            slug_categoria = slugify(nombre_categoria)
            categoria, created = Categoria.objects.update_or_create(
                slug=slug_categoria,
                defaults={"nombre": nombre_categoria, "activa": True},
            )
            categorias_activas.append(categoria)
            if created:
                categorias_creadas += 1
            else:
                categorias_actualizadas += 1

        for categoria in categorias_activas:
            productos = self.PRODUCTOS_POR_CATEGORIA.get(categoria.nombre, [])
            for nombre, descripcion, precio, stock in productos:
                slug_producto = f"{slugify(nombre)}-{categoria.slug}"
                _, created = Producto.objects.update_or_create(
                    slug=slug_producto,
                    defaults={
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "precio": precio,
                        "stock": stock,
                        "imagen": f"https://picsum.photos/seed/{slug_producto}/800/600",
                        "activo": True,
                        "categoria": categoria,
                    },
                )
                if created:
                    productos_creados += 1
                else:
                    productos_actualizados += 1

        self.stdout.write(self.style.SUCCESS("Carga de productos de prueba completada."))
        self.stdout.write(
            f"Categorias -> creadas: {categorias_creadas}, actualizadas/reutilizadas: {categorias_actualizadas}"
        )
        self.stdout.write(
            f"Productos -> creados: {productos_creados}, actualizados/reutilizados: {productos_actualizados}"
        )
