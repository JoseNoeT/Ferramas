from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Producto
from apps.credito.models import CuentaCredito
from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro
from apps.puntos.models import CuentaPuntos
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea/actualiza datos demo idempotentes para desarrollo y despliegue."

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
    ]

    DEMO_PRODUCTS = [
        {
            "nombre": "Martillo de 1kg",
            "descripcion": "Martillo de acero para trabajos generales de obra.",
            "precio": Decimal("25990.00"),
            "stock": 30,
            "categoria": "Herramientas",
        },
        {
            "nombre": "Destornillador Phillips #2",
            "descripcion": "Destornillador con mango ergonomico para fijaciones comunes.",
            "precio": Decimal("7990.00"),
            "stock": 45,
            "categoria": "Herramientas",
        },
        {
            "nombre": "Taladro Percutor 650W",
            "descripcion": "Taladro percutor electrico para uso domiciliario y profesional ligero.",
            "precio": Decimal("59990.00"),
            "stock": 18,
            "categoria": "Herramientas",
        },
        {
            "nombre": "Cable electrico 2.5 mm 100 metros",
            "descripcion": "Rollo de cable para instalaciones electricas residenciales.",
            "precio": Decimal("48990.00"),
            "stock": 16,
            "categoria": "Materiales Electricos",
        },
        {
            "nombre": "Pintura Latex Blanca 1 Galon",
            "descripcion": "Pintura interior de secado rapido con alto cubrimiento.",
            "precio": Decimal("22990.00"),
            "stock": 22,
            "categoria": "Pinturas",
        },
        {
            "nombre": "Casco de seguridad con ajuste",
            "descripcion": "Casco certificado con sistema de ajuste para faenas.",
            "precio": Decimal("10990.00"),
            "stock": 40,
            "categoria": "Seguridad",
        },
        {
            "nombre": "Guantes de seguridad",
            "descripcion": "Guantes resistentes para proteccion en trabajos manuales.",
            "precio": Decimal("4990.00"),
            "stock": 70,
            "categoria": "Seguridad",
        },
        {
            "nombre": "Tornillos Acero 3 pulgadas",
            "descripcion": "Caja de tornillos de acero galvanizado para estructuras de madera.",
            "precio": Decimal("5990.00"),
            "stock": 120,
            "categoria": "Materiales Electricos",
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
                    "imagen": f"https://picsum.photos/seed/{slug}/800/600",
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
