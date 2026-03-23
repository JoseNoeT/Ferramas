#!/usr/bin/env python
"""Script para poblar la base de datos con datos de prueba."""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.catalogo.models import Categoria, Producto
from apps.usuarios.models import Usuario

# Limpiar datos anteriores
Usuario.objects.filter(email='cliente@test.com').delete()

# Crear un usuario de prueba
usuario_prueba = Usuario.objects.create_user(
    email='cliente@test.com',
    password='Test123456'
)
print(f"✓ Usuario de prueba creado: cliente@test.com")

# Crear categorías
cat_herramientas = Categoria.objects.create(
    nombre='Herramientas',
    slug='herramientas',
    activa=True
)

cat_materiales = Categoria.objects.create(
    nombre='Materiales',
    slug='materiales',
    activa=True
)
print(f"✓ Categorías creadas: {Categoria.objects.count()}")

# Crear productos
Producto.objects.create(
    nombre='Martillo de 1kg',
    slug='martillo-1kg',
    descripcion='Martillo de claw de 1 kilogramo, ideal para obras',
    precio=25000,
    stock=15,
    imagen='',
    activo=True,
    categoria=cat_herramientas
)

Producto.objects.create(
    nombre='Destornillador Phillips #2',
    slug='destornillador-phillips-2',
    descripcion='Destornillador de punta Phillips número 2',
    precio=8000,
    stock=32,
    imagen='',
    activo=True,
    categoria=cat_herramientas
)

Producto.objects.create(
    nombre='Tablón de Madera 2x4',
    slug='tablon-madera-2x4',
    descripcion='Tablón de madera pino 2x4 pulgadas, 3 metros',
    precio=12000,
    stock=20,
    imagen='',
    activo=True,
    categoria=cat_materiales
)

Producto.objects.create(
    nombre='Tornillos Acero 3 pulgadas',
    slug='tornillos-acero-3',
    descripcion='Paquete de 100 tornillos de acero de 3 pulgadas',
    precio=5500,
    stock=50,
    imagen='',
    activo=True,
    categoria=cat_materiales
)

print(f"✓ Productos creados: {Producto.objects.count()}")
print("\n✓ Datos de prueba poblados correctamente")
print("  email: cliente@test.com")
print("  password: Test123456")
