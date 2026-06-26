from django.apps import apps
from django.urls import NoReverseMatch, reverse
from django.db.models import Count, Sum
from django.utils import timezone

from apps.catalogo.models import Categoria, Producto
from apps.usuarios.models import Usuario


def obtener_dashboard_indicadores():
    """
    Construye el contexto completo para el dashboard administrador.
    Debe conservar exactamente las keys que usan las plantillas actuales.
    """
    stock_bajo_limite = 5

    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(activo=True).count()
    productos_inactivos = Producto.objects.filter(activo=False).count()
    productos_stock_bajo = Producto.objects.filter(stock__gt=0, stock__lte=stock_bajo_limite).count()
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    total_categorias = Categoria.objects.count()
    total_usuarios = Usuario.objects.count()

    usuarios_por_rol = {
        "clientes": Usuario.objects.filter(rol=Usuario.Rol.CLIENTE).count(),
        "admins": Usuario.objects.filter(rol=Usuario.Rol.ADMIN).count(),
        "vendedores": Usuario.objects.filter(rol=Usuario.Rol.VENDEDOR).count(),
        "bodegueros": Usuario.objects.filter(rol=Usuario.Rol.BODEGUERO).count(),
        "contadores": Usuario.objects.filter(rol=Usuario.Rol.CONTADOR).count(),
    }

    categorias_destacadas = list(
        Categoria.objects.annotate(total_productos=Count("productos"))
        .order_by("-total_productos", "nombre")[:5]
    )
    productos_recientes = list(
        Producto.objects.select_related("categoria").order_by("-fecha_creacion")[:6]
    )

    # Pedidos/ventas: intentar obtener el modelo Pedido dinámicamente
    total_pedidos = 0
    pedidos_hoy = 0
    pedidos_pendientes = 0
    total_ventas = 0
    pedidos_disponibles = False
    try:
        Pedido = apps.get_model("pedidos", "Pedido")
        pedidos_disponibles = Pedido is not None
    except LookupError:
        Pedido = None

    if Pedido is not None:
        campo_estado = None
        campo_total = None
        campo_fecha = None
        nombres_campos = {field.name for field in Pedido._meta.get_fields() if hasattr(field, "name")}

        if "estado" in nombres_campos:
            campo_estado = "estado"
        if "total" in nombres_campos:
            campo_total = "total"
        if "creado_en" in nombres_campos:
            campo_fecha = "creado_en"
        elif "fecha_creacion" in nombres_campos:
            campo_fecha = "fecha_creacion"

        try:
            pedidos_qs = Pedido.objects.all()
            total_pedidos = pedidos_qs.count()

            if campo_fecha:
                pedidos_hoy = pedidos_qs.filter(**{f"{campo_fecha}__date": timezone.localdate()}).count()

            if campo_estado:
                estados_pendientes = ["generado", "aprobado", "en_preparacion"]
                pedidos_pendientes = pedidos_qs.filter(**{f"{campo_estado}__in": estados_pendientes}).count()

            if campo_total:
                total_ventas = pedidos_qs.aggregate(total=Sum(campo_total)).get("total") or 0
        except Exception:
            pedidos_disponibles = False
            total_pedidos = 0
            pedidos_hoy = 0
            pedidos_pendientes = 0
            total_ventas = 0

    # Determinar disponibilidad del módulo reportes (mantener la misma comprobación que tenía la vista)
    reportes_disponibles = True
    try:
        reverse("reportes_dashboard")
    except NoReverseMatch:
        reportes_disponibles = False

    # Construir alertas (misma lógica que antes)
    alertas = []
    if productos_sin_stock:
        alertas.append(
            {
                "titulo": "Productos sin stock",
                "detalle": f"{productos_sin_stock} productos agotados requieren reposición inmediata.",
                "tipo": "critica",
            }
        )
    if productos_stock_bajo:
        alertas.append(
            {
                "titulo": "Stock bajo detectado",
                "detalle": f"{productos_stock_bajo} productos están bajo el umbral de {stock_bajo_limite} unidades.",
                "tipo": "advertencia",
            }
        )
    if pedidos_pendientes:
        alertas.append(
            {
                "titulo": "Pedidos pendientes",
                "detalle": f"Hay {pedidos_pendientes} pedidos que requieren seguimiento operativo.",
                "tipo": "info",
            }
        )
    if not alertas:
        alertas.append(
            {
                "titulo": "Operación estable",
                "detalle": "No hay alertas críticas registradas en este momento.",
                "tipo": "success",
            }
        )

    modulos_admin = [
        {
            "titulo": "Productos",
            "descripcion": "Gestiona catálogo, precios, stock y disponibilidad comercial.",
            "cantidad": total_productos,
            "meta": f"{productos_activos} activos · {productos_inactivos} inactivos",
            "url": "admin_productos_dashboard",
        },
        {
            "titulo": "Categorias",
            "descripcion": "Ordena la estructura del catálogo y crea nuevas categorías.",
            "cantidad": total_categorias,
            "meta": "Clasificación principal del catálogo",
            "url": "admin_categorias_dashboard",
        },
        {
            "titulo": "Usuarios internos",
            "descripcion": "Administra accesos internos, credenciales y roles del sistema.",
            "cantidad": Usuario.objects.exclude(rol=Usuario.Rol.CLIENTE).count(),
            "meta": f"{usuarios_por_rol['admins']} admins · {usuarios_por_rol['vendedores']} vendedores",
            "url": "admin_usuarios_dashboard",
        },
        {
            "titulo": "Clientes",
            "descripcion": "Lista de clientes registrados en la plataforma.",
            "cantidad": Usuario.objects.filter(rol=Usuario.Rol.CLIENTE).count(),
            "meta": f"{usuarios_por_rol['clientes']} clientes",
            "url": "admin_clientes",
        },
    ]

    if reportes_disponibles:
        modulos_admin.append(
            {
                "titulo": "Reportes",
                "descripcion": "Consulta indicadores y reportes consolidados del negocio.",
                "cantidad": total_pedidos,
                "meta": "Acceso a información estratégica",
                "url": "reportes_dashboard",
            }
        )

    # Añadir tarjeta Maestros/PYME si la ruta admin_maestros está disponible
    maestros_disponibles = True
    try:
        reverse("admin_maestros")
    except NoReverseMatch:
        maestros_disponibles = False

    if maestros_disponibles:
        from apps.maestros.models import PerfilMaestroPyme

        total_maestros = PerfilMaestroPyme.objects.count()
        modulos_admin.append(
            {
                "titulo": "Maestros/PYME",
                "descripcion": "Gestiona perfiles Maestro/PYME y solicitudes.",
                "cantidad": total_maestros,
                "meta": f"{total_maestros} perfiles",
                "url": "admin_maestros",
            }
        )

    total_usuarios_internos = (
        usuarios_por_rol["admins"]
        + usuarios_por_rol["vendedores"]
        + usuarios_por_rol["bodegueros"]
        + usuarios_por_rol["contadores"]
    )
    promedio_venta = (total_ventas / total_pedidos) if total_pedidos else 0
    porcentaje_productos_activos = round((productos_activos / total_productos) * 100) if total_productos else 0
    porcentaje_stock_saludable = round(
        ((total_productos - productos_stock_bajo - productos_sin_stock) / total_productos) * 100
    ) if total_productos else 0
    porcentaje_usuarios_internos = round((total_usuarios_internos / total_usuarios) * 100) if total_usuarios else 0
    porcentaje_pedidos_pendientes = round((pedidos_pendientes / total_pedidos) * 100) if total_pedidos else 0

    indicadores_operativos = [
        {
            "titulo": "Catalogo activo",
            "valor": f"{porcentaje_productos_activos}%",
            "detalle": f"{productos_activos} de {total_productos} productos publicados.",
            "porcentaje": porcentaje_productos_activos,
        },
        {
            "titulo": "Salud de stock",
            "valor": f"{porcentaje_stock_saludable}%",
            "detalle": f"{productos_sin_stock} sin stock y {productos_stock_bajo} con stock bajo.",
            "porcentaje": porcentaje_stock_saludable,
        },
        {
            "titulo": "Usuarios internos",
            "valor": f"{porcentaje_usuarios_internos}%",
            "detalle": f"{total_usuarios_internos} internos sobre {total_usuarios} usuarios totales.",
            "porcentaje": porcentaje_usuarios_internos,
        },
        {
            "titulo": "Carga operativa",
            "valor": f"{porcentaje_pedidos_pendientes}%",
            "detalle": f"{pedidos_pendientes} pedidos pendientes de un total de {total_pedidos}.",
            "porcentaje": porcentaje_pedidos_pendientes,
        },
    ]

    context = {
        "total_productos": total_productos,
        "productos_activos": productos_activos,
        "productos_inactivos": productos_inactivos,
        "productos_stock_bajo": productos_stock_bajo,
        "productos_sin_stock": productos_sin_stock,
        "total_categorias": total_categorias,
        "total_usuarios": total_usuarios,
        "usuarios_por_rol": usuarios_por_rol,
        "total_pedidos": total_pedidos,
        "pedidos_hoy": pedidos_hoy,
        "pedidos_pendientes": pedidos_pendientes,
        "total_ventas": total_ventas,
        "pedidos_disponibles": pedidos_disponibles,
        "categorias_destacadas": categorias_destacadas,
        "productos_recientes": productos_recientes,
        "modulos_admin": modulos_admin,
        "alertas": alertas,
        "stock_bajo_limite": stock_bajo_limite,
        "total_usuarios_internos": total_usuarios_internos,
        "promedio_venta": promedio_venta,
        "indicadores_operativos": indicadores_operativos,
    }
    return context
