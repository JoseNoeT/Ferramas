from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Producto
from apps.credito.models import CuentaCredito
from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro
from apps.puntos.models import CuentaPuntos
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea/actualiza datos demo idempotentes para desarrollo y despliegue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-demo",
            action="store_true",
            dest="force_demo",
            help="Forzar ejecución de seed_demo aun cuando settings.DEBUG == False (usar con precaución).",
        )

    DEMO_USERS = [
        {
            "email": "admin.interno@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "vendedor@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.VENDEDOR,
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "bodeguero@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.BODEGUERO,
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "contador@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.CONTADOR,
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "cliente@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.CLIENTE,
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "maestro@test.com",
            "password": "Test123456",
            "rol": Usuario.Rol.CLIENTE,
            "is_staff": False,
            "is_superuser": False,
        },
    ]

    DEMO_CATEGORIES = [
        "Herramientas",
        "Pinturas",
        "Materiales Electricos",
        "Seguridad",
        "Construccion",
        "Madera y Materiales",
    ]

    DEMO_PRODUCTS = [
        # Herramientas
        {
            "nombre": "Martillo de 1kg",
            "descripcion": "Martillo de acero para trabajos generales de obra.",
            "precio": Decimal("25990.00"),
            "stock": 30,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/martillo-1kg.png",
        },
        {
            "nombre": "Destornillador Phillips #2",
            "descripcion": "Destornillador con mango ergonomico para fijaciones comunes.",
            "precio": Decimal("7990.00"),
            "stock": 45,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/destornillador-phillips-2.png",
        },
        {
            "nombre": "Taladro Percutor 650W",
            "descripcion": "Taladro percutor electrico para uso domiciliario y profesional ligero.",
            "precio": Decimal("59990.00"),
            "stock": 18,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/taladro-percutor-650w.png",
        },
        {
            "nombre": "Atornillador Inalambrico 12V",
            "descripcion": "Atornillador inalambrico con bateria de litio y dos velocidades.",
            "precio": Decimal("49990.00"),
            "stock": 20,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/atornillador-inalambrico.png",
        },
        {
            "nombre": "Esmeril Angular 750W",
            "descripcion": "Esmeril angular para corte y desbaste de metal y piedra.",
            "precio": Decimal("44990.00"),
            "stock": 15,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/esmeril-angular-750w.png",
        },
        {
            "nombre": "Sierra Caladora 500W",
            "descripcion": "Sierra caladora electrica para cortes en madera, plastico y metal fino.",
            "precio": Decimal("54990.00"),
            "stock": 12,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/sierra-caladora-500w.png",
        },
        {
            "nombre": "Lijadora Orbital 300W",
            "descripcion": "Lijadora orbital para acabado fino en superficies de madera.",
            "precio": Decimal("39990.00"),
            "stock": 14,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/lijadora-orbital-300w.png",
        },
        {
            "nombre": "Serrucho Carpintero 22 pulgadas",
            "descripcion": "Serrucho de acero templado para corte de madera en general.",
            "precio": Decimal("12990.00"),
            "stock": 35,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/serrucho-carpintero.png",
        },
        {
            "nombre": "Llave Ajustable 10 pulgadas",
            "descripcion": "Llave ajustable de acero cromado para tuercas y pernos.",
            "precio": Decimal("9990.00"),
            "stock": 50,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/llave-ajustable-10.png",
        },
        {
            "nombre": "Nivel Burbuja 40cm",
            "descripcion": "Nivel de aluminio con tres ampollas para medicion horizontal y vertical.",
            "precio": Decimal("8990.00"),
            "stock": 40,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/nivel-burbuja-40cm.png",
        },
        {
            "nombre": "Alicate Universal 8 pulgadas",
            "descripcion": "Alicate multiuso con mango aislado para trabajos electricos y mecanicos.",
            "precio": Decimal("6990.00"),
            "stock": 55,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/alicate-universal.png",
        },
        {
            "nombre": "Huincha de Medir 5 metros",
            "descripcion": "Cinta metrica retractil de 5 metros con freno de seguridad.",
            "precio": Decimal("4990.00"),
            "stock": 80,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/huincha-medir-5m.png",
        },
        {
            "nombre": "Cutter Profesional 18mm",
            "descripcion": "Cutter de hoja ancha con bloqueo metalico para cortes precisos.",
            "precio": Decimal("3990.00"),
            "stock": 90,
            "categoria": "Herramientas",
            "imagen": "/static/img/productos/cutter-profesional.png",
        },
        # Materiales Electricos
        {
            "nombre": "Cable Electrico 2.5mm 100 metros",
            "descripcion": "Rollo de cable para instalaciones electricas residenciales.",
            "precio": Decimal("48990.00"),
            "stock": 16,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/cable-electrico-25mm.png",
        },
        {
            "nombre": "Tornillos Acero 3 pulgadas",
            "descripcion": "Caja de tornillos de acero galvanizado para estructuras de madera.",
            "precio": Decimal("5990.00"),
            "stock": 120,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/tornillos-acero.png",
        },
        {
            "nombre": "Ampolleta LED 12W",
            "descripcion": "Ampolleta LED de bajo consumo con base E27 y luz blanca fria.",
            "precio": Decimal("2990.00"),
            "stock": 200,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/ampolleta-led-12w.png",
        },
        {
            "nombre": "Enchufe Hembra Simple",
            "descripcion": "Enchufe mural simple con toma de tierra para instalacion embutida.",
            "precio": Decimal("1990.00"),
            "stock": 150,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/enchufe-hembra-simple.png",
        },
        {
            "nombre": "Interruptor Simple",
            "descripcion": "Interruptor de luz unipolar para instalacion embutida en muro.",
            "precio": Decimal("1990.00"),
            "stock": 150,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/interruptor-simple.png",
        },
        {
            "nombre": "Automatico Termomagnetico 10A",
            "descripcion": "Disyuntor termomagnetico monofasico 10A para tablero electrico.",
            "precio": Decimal("8990.00"),
            "stock": 60,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/automatico-10a.png",
        },
        {
            "nombre": "Caja de Derivacion Electrica",
            "descripcion": "Caja plastica para derivaciones electricas con tapa y prensaestopas.",
            "precio": Decimal("3490.00"),
            "stock": 80,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/caja-derivacion-electrica.png",
        },
        {
            "nombre": "Tubo Conduit 20mm 3 metros",
            "descripcion": "Tubo PVC rigido para canalizacion de instalaciones electricas.",
            "precio": Decimal("2490.00"),
            "stock": 100,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/tubo-conduit-20mm.png",
        },
        {
            "nombre": "Cinta Aislante 20 metros",
            "descripcion": "Cinta aislante PVC negra resistente al calor y la humedad.",
            "precio": Decimal("990.00"),
            "stock": 300,
            "categoria": "Materiales Electricos",
            "imagen": "/static/img/productos/cinta-aislante.png",
        },
        # Pinturas
        {
            "nombre": "Pintura Latex Blanca 1 Galon",
            "descripcion": "Pintura interior de secado rapido con alto cubrimiento.",
            "precio": Decimal("22990.00"),
            "stock": 22,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/pintura-latex-blanca.png",
        },
        {
            "nombre": "Esmalte Sintetico Blanco 1 Litro",
            "descripcion": "Esmalte de alto brillo para madera y metal, secado rapido.",
            "precio": Decimal("12990.00"),
            "stock": 30,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/esmalte-sintetico-blanco.png",
        },
        {
            "nombre": "Masilla para Muro 4kg",
            "descripcion": "Masilla acrilica para nivelar y reparar superficies de muro.",
            "precio": Decimal("9990.00"),
            "stock": 40,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/masilla-muro.png",
        },
        {
            "nombre": "Sellador Acrilico 300ml",
            "descripcion": "Sellador flexible para juntas y fisuras en muros y cielos.",
            "precio": Decimal("4990.00"),
            "stock": 60,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/sellador-acrilico.png",
        },
        {
            "nombre": "Rodillo Felpa 23cm",
            "descripcion": "Rodillo de felpa para aplicacion de pintura latex en muros.",
            "precio": Decimal("5990.00"),
            "stock": 50,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/rodillo-felpa.png",
        },
        {
            "nombre": "Rodillo de Pintura con Mango",
            "descripcion": "Kit rodillo con mango extensible para pintura de cielos y muros altos.",
            "precio": Decimal("8990.00"),
            "stock": 35,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/rodillo-pintura.png",
        },
        {
            "nombre": "Espatula Metalica 10cm",
            "descripcion": "Espatula de acero flexible para aplicar masilla y raspar superficies.",
            "precio": Decimal("2990.00"),
            "stock": 70,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/espatula-metalica.png",
        },
        {
            "nombre": "Brocha de Pintura 3 pulgadas",
            "descripcion": "Brocha con cerdas naturales para pintura, barniz y esmalte.",
            "precio": Decimal("3490.00"),
            "stock": 60,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/brocha-pintura.png",
        },
        {
            "nombre": "Bandeja de Pintura Plastica",
            "descripcion": "Bandeja plastica con rejilla para escurrir rodillo de pintura.",
            "precio": Decimal("2490.00"),
            "stock": 55,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/bandeja-pintura.png",
        },
        {
            "nombre": "Lija de Muro Grano 120",
            "descripcion": "Lija de agua grano 120 para lijar muros y superficies preparadas.",
            "precio": Decimal("490.00"),
            "stock": 500,
            "categoria": "Pinturas",
            "imagen": "/static/img/productos/lija-muro-grano-120.png",
        },
        # Seguridad
        {
            "nombre": "Casco de Seguridad con Ajuste",
            "descripcion": "Casco certificado con sistema de ajuste para faenas.",
            "precio": Decimal("10990.00"),
            "stock": 40,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/casco-seguridad.png",
        },
        {
            "nombre": "Guantes de Seguridad",
            "descripcion": "Guantes resistentes para proteccion en trabajos manuales.",
            "precio": Decimal("4990.00"),
            "stock": 70,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/guantes-seguridad.png",
        },
        {
            "nombre": "Arnes de Seguridad Completo",
            "descripcion": "Arnes anticaida con puntos de anclaje dorsal y esternal certificado.",
            "precio": Decimal("79990.00"),
            "stock": 10,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/arnes-seguridad.png",
        },
        {
            "nombre": "Botas de Seguridad Punta Acero",
            "descripcion": "Bota de cuero con puntera de acero y planta antideslizante.",
            "precio": Decimal("39990.00"),
            "stock": 25,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/botas-seguridad.png",
        },
        {
            "nombre": "Protector Auditivo",
            "descripcion": "Orejeras de copa para proteccion contra ruido en faenas.",
            "precio": Decimal("8990.00"),
            "stock": 45,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/protector-auditivo.png",
        },
        {
            "nombre": "Cono de Seguridad Vial 70cm",
            "descripcion": "Cono reflectante naranja para delimitacion de zonas de trabajo.",
            "precio": Decimal("6990.00"),
            "stock": 60,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/cono-seguridad.png",
        },
        {
            "nombre": "Mascarilla Antipolvo",
            "descripcion": "Mascarilla desechable con filtro N95 para polvo y particulas finas.",
            "precio": Decimal("1990.00"),
            "stock": 200,
            "categoria": "Seguridad",
            "imagen": "/static/img/productos/mascarilla-polvo.png",
        },
        # Construccion
        {
            "nombre": "Cemento Portland 25kg",
            "descripcion": "Saco de cemento Portland para hormigon y mortero de obra.",
            "precio": Decimal("7990.00"),
            "stock": 80,
            "categoria": "Construccion",
            "imagen": "/static/img/productos/cemento-25kg.png",
        },
        {
            "nombre": "Arena Fina 25kg",
            "descripcion": "Saco de arena fina lavada para morteros y terminaciones.",
            "precio": Decimal("3990.00"),
            "stock": 100,
            "categoria": "Construccion",
            "imagen": "/static/img/productos/saco-arena-fina.png",
        },
        {
            "nombre": "Gravilla Gruesa 25kg",
            "descripcion": "Saco de gravilla gruesa para hormigon y drenaje.",
            "precio": Decimal("3490.00"),
            "stock": 100,
            "categoria": "Construccion",
            "imagen": "/static/img/productos/saco-gravilla.png",
        },
        # Madera y Materiales
        {
            "nombre": "Madera Cepillada 2x4 3 metros",
            "descripcion": "Pieza de madera pino cepillada seca para estructura y terminaciones.",
            "precio": Decimal("5990.00"),
            "stock": 60,
            "categoria": "Madera y Materiales",
            "imagen": "/static/img/productos/madera-cepillada.png",
        },
        {
            "nombre": "Plancha OSB 11mm 1.22x2.44m",
            "descripcion": "Panel OSB estructural para revestimiento de muros y cubierta.",
            "precio": Decimal("19990.00"),
            "stock": 30,
            "categoria": "Madera y Materiales",
            "imagen": "/static/img/productos/plancha-osb-11mm.png",
        },
        {
            "nombre": "Volcanita Standar 10mm 1.2x2.4m",
            "descripcion": "Placa de yeso para tabiqueria y cielos en interiores.",
            "precio": Decimal("14990.00"),
            "stock": 40,
            "categoria": "Madera y Materiales",
            "imagen": "/static/img/productos/volcanita-10mm.png",
        },
    ]

    DEMO_SERVICES = [
        {
            "titulo": "Instalacion electrica domiciliaria",
            "descripcion": "Asesoria e instalacion de circuitos, enchufes y luminarias.",
            "rubro": "Electricidad",
            "zona_atencion": "Santiago",
            "precio_referencial": Decimal("45000.00"),
        },
        {
            "titulo": "Reparaciones de gasfiteria",
            "descripcion": "Reparacion de fugas, cambio de llaves y mejoras sanitarias.",
            "rubro": "Gasfiteria",
            "zona_atencion": "Santiago",
            "precio_referencial": Decimal("38000.00"),
        },
        {
            "titulo": "Pintura interior y terminaciones",
            "descripcion": "Aplicacion de pintura interior y terminaciones finas de muro.",
            "rubro": "Pinturas",
            "zona_atencion": "Santiago",
            "precio_referencial": Decimal("52000.00"),
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        # Protección: en entornos no DEBUG exigir flag explícito
        force = options.get("force_demo", False)
        if not settings.DEBUG and not force:
            raise CommandError(
                "Seed demo bloqueado: settings.DEBUG es False. Para forzar la ejecución use --force-demo (no recomendado en producción)."
            )
        summary = {
            "usuarios_creados": 0,
            "usuarios_actualizados": 0,
            "categorias_creadas": 0,
            "categorias_actualizadas": 0,
            "productos_creados": 0,
            "productos_actualizados": 0,
            "perfil_maestro_creado": 0,
            "perfil_maestro_actualizado": 0,
            "servicios_creados": 0,
            "servicios_actualizados": 0,
            "cuentas_credito_creadas": 0,
            "cuentas_credito_actualizadas": 0,
            "cuentas_puntos_creadas": 0,
            "cuentas_puntos_actualizadas": 0,
        }

        users = self._seed_users(summary)
        categories = self._seed_categories(summary)
        self._seed_products(summary, categories)

        maestro_user = users["maestro@test.com"]
        perfil_maestro = self._seed_maestro_profile(summary, maestro_user)
        self._seed_maestro_services(summary, perfil_maestro)

        self._seed_credit_account(summary, perfil_maestro)
        self._seed_points_account(summary, users["cliente@test.com"])

        self._print_summary(summary)

    def _seed_users(self, summary):
        seeded = {}
        for item in self.DEMO_USERS:
            email = item["email"]
            defaults = {
                "rol": item["rol"],
                "activo": True,
                "is_active": True,
                "is_staff": item["is_staff"],
                "is_superuser": item["is_superuser"],
            }
            user, created = Usuario.objects.get_or_create(email=email, defaults=defaults)
            if created:
                summary["usuarios_creados"] += 1
            else:
                changed = False
                for field, value in defaults.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        changed = True
                if changed:
                    user.save(update_fields=list(defaults.keys()))
                summary["usuarios_actualizados"] += 1

            user.set_password(item["password"])
            user.save(update_fields=["password"])
            seeded[email] = user
        return seeded

    def _seed_categories(self, summary):
        categories = {}
        for name in self.DEMO_CATEGORIES:
            slug = slugify(name)
            categoria, created = Categoria.objects.update_or_create(
                slug=slug,
                defaults={"nombre": name, "activa": True},
            )
            if created:
                summary["categorias_creadas"] += 1
            else:
                summary["categorias_actualizadas"] += 1
            categories[name] = categoria
        return categories

    def _seed_products(self, summary, categories):
        for data in self.DEMO_PRODUCTS:
            slug = slugify(data["nombre"])
            categoria = categories[data["categoria"]]
            _, created = Producto.objects.update_or_create(
                slug=slug,
                defaults={
                    "nombre": data["nombre"],
                    "descripcion": data["descripcion"],
                    "precio": data["precio"],
                    "stock": data["stock"],
                    "imagen": data.get("imagen", "/static/img/productos/producto-default.png"),
                    "activo": True,
                    "categoria": categoria,
                },
            )
            if created:
                summary["productos_creados"] += 1
            else:
                summary["productos_actualizados"] += 1

    def _seed_maestro_profile(self, summary, maestro_user):
        defaults = {
            "tipo": PerfilMaestroPyme.Tipo.MAESTRO,
            "rut": "11111111-1",
            "rubro": "Servicios para el hogar",
            "oficio": "Tecnico integral",
            "nombre_empresa": "Maestro Demo",
            "telefono": "+56911111111",
            "direccion": "Av. Demo 123, Santiago",
            "estado": PerfilMaestroPyme.Estado.APROBADO,
        }
        perfil, created = PerfilMaestroPyme.objects.update_or_create(
            usuario=maestro_user,
            defaults=defaults,
        )
        if created:
            summary["perfil_maestro_creado"] += 1
        else:
            summary["perfil_maestro_actualizado"] += 1
        return perfil

    def _seed_maestro_services(self, summary, perfil_maestro):
        for service in self.DEMO_SERVICES:
            existing = (
                ServicioMaestro.objects.filter(maestro=perfil_maestro, titulo=service["titulo"])
                .order_by("id")
                .first()
            )
            if existing:
                existing.descripcion = service["descripcion"]
                existing.rubro = service["rubro"]
                existing.zona_atencion = service["zona_atencion"]
                existing.precio_referencial = service["precio_referencial"]
                existing.activo = True
                existing.save(
                    update_fields=[
                        "descripcion",
                        "rubro",
                        "zona_atencion",
                        "precio_referencial",
                        "activo",
                        "actualizado_en",
                    ]
                )
                summary["servicios_actualizados"] += 1
            else:
                ServicioMaestro.objects.create(
                    maestro=perfil_maestro,
                    titulo=service["titulo"],
                    descripcion=service["descripcion"],
                    rubro=service["rubro"],
                    zona_atencion=service["zona_atencion"],
                    precio_referencial=service["precio_referencial"],
                    activo=True,
                )
                summary["servicios_creados"] += 1

    def _seed_credit_account(self, summary, perfil_maestro):
        _, created = CuentaCredito.objects.update_or_create(
            maestro=perfil_maestro,
            defaults={
                "cupo_aprobado": Decimal("250000.00"),
                "saldo_usado": Decimal("0.00"),
                "estado": CuentaCredito.Estado.ACTIVA,
            },
        )
        if created:
            summary["cuentas_credito_creadas"] += 1
        else:
            summary["cuentas_credito_actualizadas"] += 1

    def _seed_points_account(self, summary, cliente_user):
        _, created = CuentaPuntos.objects.update_or_create(
            usuario=cliente_user,
            defaults={"saldo": 1000},
        )
        if created:
            summary["cuentas_puntos_creadas"] += 1
        else:
            summary["cuentas_puntos_actualizadas"] += 1

    def _print_summary(self, summary):
        self.stdout.write(self.style.SUCCESS("Seed demo completado."))
        self.stdout.write(
            f"Usuarios -> creados: {summary['usuarios_creados']}, actualizados/reutilizados: {summary['usuarios_actualizados']}"
        )
        self.stdout.write(
            f"Categorias -> creadas: {summary['categorias_creadas']}, actualizadas/reutilizadas: {summary['categorias_actualizadas']}"
        )
        self.stdout.write(
            f"Productos -> creados: {summary['productos_creados']}, actualizados/reutilizados: {summary['productos_actualizados']}"
        )
        self.stdout.write(
            "Perfil Maestro/PYME -> "
            f"creado: {summary['perfil_maestro_creado']}, "
            f"actualizado/reutilizado: {summary['perfil_maestro_actualizado']}"
        )
        self.stdout.write(
            f"Servicios Maestro -> creados: {summary['servicios_creados']}, actualizados/reutilizados: {summary['servicios_actualizados']}"
        )
        self.stdout.write(
            "Cuenta Credito -> "
            f"creada: {summary['cuentas_credito_creadas']}, "
            f"actualizada/reutilizada: {summary['cuentas_credito_actualizadas']}"
        )
        self.stdout.write(
            "Cuenta Puntos -> "
            f"creada: {summary['cuentas_puntos_creadas']}, "
            f"actualizada/reutilizada: {summary['cuentas_puntos_actualizadas']}"
        )

        self.stdout.write("Credenciales demo:")
        for item in self.DEMO_USERS:
            self.stdout.write(f"  - {item['email']} / {item['password']} ({item['rol']})")
