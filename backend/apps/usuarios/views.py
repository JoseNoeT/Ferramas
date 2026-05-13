import csv
from datetime import date

from apps.maestros.models import PerfilMaestroPyme
from .forms import PerfilUsuarioForm

# Vista para mostrar y editar el perfil del usuario autenticado
from django.contrib.auth.decorators import login_required

@login_required
def perfil_usuario_view(request):
    user = request.user
    perfil_maestro_pyme = None
    es_maestro_pyme = False
    maestro_aprobado = False

    # Buscar perfil Maestro/PYME asociado si existe
    try:
        perfil_maestro_pyme = user.perfil_maestro_pyme
        es_maestro_pyme = True
        maestro_aprobado = perfil_maestro_pyme.estado == PerfilMaestroPyme.Estado.APROBADO
    except PerfilMaestroPyme.DoesNotExist:
        perfil_maestro_pyme = None
        es_maestro_pyme = False
        maestro_aprobado = False

    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil_usuario")
    else:
        form = PerfilUsuarioForm(instance=user)

    context = {
        "form": form,
        "perfil_maestro_pyme": perfil_maestro_pyme,
        "es_maestro_pyme": es_maestro_pyme,
        "maestro_aprobado": maestro_aprobado,
        "user": user,
    }
    return render(request, "pages/perfil.html", context)
from django.contrib import messages
from django.db.models import Case, Count, DecimalField, F, Q, Sum, When
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from apps.catalogo import services as catalogo_services
from apps.catalogo.models import Categoria, Producto

from .forms import LoginForm, RegistroForm, UsuarioInternoCreateForm, UsuarioInternoUpdateForm
from .models import Usuario
from .services import (
    autenticar_usuario,
    cambiar_estado_usuario,
    crear_usuario_interno,
    listar_usuarios_internos,
    registrar_usuario,
    actualizar_usuario_interno,
)


def _obtener_redireccion_segura(request: HttpRequest, destino: str | None) -> str | None:
    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return None


def _requiere_admin(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol != Usuario.Rol.ADMIN:
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
        return view_func(request, *args, **kwargs)

    return wrapper


def _ruta_dashboard_por_rol(rol: str) -> str:
    if rol == Usuario.Rol.ADMIN:
        return "admin_dashboard"
    if rol == Usuario.Rol.VENDEDOR:
        return "vendedor_dashboard"
    if rol == Usuario.Rol.BODEGUERO:
        return "bodeguero_dashboard"
    if rol == Usuario.Rol.CONTADOR:
        return "contador_dashboard"
    return "home"


def _requiere_contador(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in [Usuario.Rol.CONTADOR, Usuario.Rol.ADMIN]:
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
        return view_func(request, *args, **kwargs)

    return wrapper


def home_view(request):
    ahora = timezone.now()
    productos_destacados = catalogo_services.obtener_productos_activos()[:4]
    productos_oferta = (
        Producto.objects.select_related("categoria")
        .filter(
            activo=True,
            en_oferta=True,
            precio_oferta__isnull=False,
            fecha_inicio_oferta__lte=ahora,
            fecha_fin_oferta__gte=ahora,
        )
        .order_by("nombre")[:10]
    )
    return render(
        request,
        "pages/home.html",
        {
            "productos_destacados": productos_destacados,
            "productos_oferta": productos_oferta,
        },
    )


def contacto_view(request):
    """Renderiza y procesa un formulario de contacto simple sin persistencia."""
    tipos_consulta = [
        ("soporte", "Solicitud de soporte"),
        ("general", "Consulta general"),
        ("colaboracion", "Colaboración / Proveedores"),
    ]
    data = {
        "nombre_completo": "",
        "email": "",
        "telefono": "",
        "mensaje": "",
        "tipo_consulta": "general",
    }

    if request.method == "POST":
        data = {
            "nombre_completo": request.POST.get("nombre_completo", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "telefono": request.POST.get("telefono", "").strip(),
            "mensaje": request.POST.get("mensaje", "").strip(),
            "tipo_consulta": request.POST.get("tipo_consulta", "general").strip(),
        }

        errores = []
        if not data["nombre_completo"]:
            errores.append("Debes ingresar tu nombre completo.")
        if not data["email"] or "@" not in data["email"]:
            errores.append("Debes ingresar un correo electrónico válido.")
        if not data["mensaje"]:
            errores.append("Debes ingresar un mensaje.")
        if data["tipo_consulta"] not in {key for key, _ in tipos_consulta}:
            errores.append("El tipo de consulta seleccionado no es válido.")

        if errores:
            messages.error(request, " ".join(errores))
        else:
            messages.success(
                request,
                "Gracias por tu mensaje. Nos pondremos en contacto contigo.",
            )
            return redirect("contacto")

    return render(
        request,
        "pages/contacto.html",
        {
            "tipos_consulta": tipos_consulta,
            "form_data": data,
        },
    )


def login_view(request):
    """Muestra el formulario de login y autentica al usuario."""
    siguiente = request.POST.get("next") or request.GET.get("next")
    redireccion_segura = _obtener_redireccion_segura(request, siguiente)

    if request.user.is_authenticated:
        return redirect(redireccion_segura or "home")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        usuario = autenticar_usuario(email, password)

        if usuario is not None:
            login(request, usuario)
            return redirect(redireccion_segura or _ruta_dashboard_por_rol(usuario.rol))
        else:
            messages.error(request, "Email o contrasena incorrectos.")

    return render(
        request,
        "pages/login.html",
        {"form": form, "next_url": redireccion_segura},
    )


def registro_view(request):
    """Muestra el formulario de registro y crea un nuevo usuario."""
    siguiente = request.POST.get("next") or request.GET.get("next")
    redireccion_segura = _obtener_redireccion_segura(request, siguiente)

    if request.user.is_authenticated:
        return redirect(redireccion_segura or "home")

    form = RegistroForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            registrar_usuario(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            messages.success(request, "Cuenta creada exitosamente. Ahora puedes iniciar sesion.")
            if redireccion_segura:
                return redirect(f"/login/?next={redireccion_segura}")
            return redirect("login")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "pages/registro.html",
        {"form": form, "next_url": redireccion_segura},
    )


def logout_view(request):
    """Cierra la sesion del usuario actual."""
    logout(request)
    return redirect("home")


@_requiere_admin
def admin_dashboard_view(request):
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

    reportes_disponibles = True
    try:
        reverse("reportes_dashboard")
    except NoReverseMatch:
        reportes_disponibles = False

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
            "titulo": "Usuarios",
            "descripcion": "Administra accesos internos, credenciales y roles del sistema.",
            "cantidad": total_usuarios,
            "meta": f"{usuarios_por_rol['admins']} admins · {usuarios_por_rol['vendedores']} vendedores",
            "url": "admin_usuarios_dashboard",
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
    return render(request, "dashboard/administrador.html", context)


@_requiere_admin
def admin_usuarios_dashboard_view(request):
    usuarios = listar_usuarios_internos()
    return render(request, "dashboard/admin-usuarios.html", {"usuarios": usuarios})


@_requiere_admin
def crear_usuario_interno_view(request):
    if request.method == "POST":
        usuario, form = crear_usuario_interno(request.POST)
        if usuario:
            messages.success(request, f"Usuario interno '{usuario.email}' creado correctamente.")
            return redirect("admin_usuarios_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = UsuarioInternoCreateForm()

    return render(
        request,
        "dashboard/admin-usuario-form.html",
        {
            "form": form,
            "titulo": "Crear usuario interno",
            "modo": "crear",
        },
    )


@_requiere_admin
def editar_usuario_interno_view(request, pk):
    usuario_obj = get_object_or_404(Usuario, pk=pk)

    if usuario_obj.rol == Usuario.Rol.CLIENTE:
        messages.error(request, "No se permite editar clientes desde este dashboard.")
        return redirect("admin_usuarios_dashboard")

    if request.method == "POST":
        usuario_actualizado, form = actualizar_usuario_interno(usuario_obj, request.POST)
        if usuario_actualizado:
            messages.success(request, f"Usuario '{usuario_actualizado.email}' actualizado.")
            return redirect("admin_usuarios_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = UsuarioInternoUpdateForm(instance=usuario_obj)

    return render(
        request,
        "dashboard/admin-usuario-form.html",
        {
            "form": form,
            "titulo": f"Editar usuario: {usuario_obj.email}",
            "modo": "editar",
            "usuario_obj": usuario_obj,
        },
    )


@_requiere_admin
def cambiar_estado_usuario_view(request, pk):
    if request.method != "POST":
        return redirect("admin_usuarios_dashboard")

    usuario_obj = get_object_or_404(Usuario, pk=pk)

    if usuario_obj.rol == Usuario.Rol.CLIENTE:
        messages.error(request, "No se permite gestionar clientes desde este dashboard.")
        return redirect("admin_usuarios_dashboard")

    nuevo_estado = request.POST.get("activo") == "1"
    cambiar_estado_usuario(usuario_obj, nuevo_estado)

    if nuevo_estado:
        messages.success(request, f"Usuario '{usuario_obj.email}' activado.")
    else:
        messages.warning(request, f"Usuario '{usuario_obj.email}' desactivado.")

    return redirect("admin_usuarios_dashboard")


@_requiere_contador
def contador_dashboard_view(request):
    Pedido = apps.get_model("pedidos", "Pedido")
    CuentaCredito = apps.get_model("credito", "CuentaCredito")
    CuotaCredito = apps.get_model("credito", "CuotaCredito")

    if request.method == "POST":
        accion = (request.POST.get("accion") or "").strip()
        cuota_id = request.POST.get("cuota_id")
        cuota = CuotaCredito.objects.select_related("cuenta").filter(pk=cuota_id).first()

        if cuota is None:
            messages.error(request, "La cuota seleccionada no existe.")
            return redirect("contador_dashboard")

        if accion == "marcar_pagada":
            if not hasattr(CuotaCredito.Estado, "PAGADA"):
                messages.error(request, "No es posible marcar pagada: el modelo no define estado PAGADA.")
                return redirect("contador_dashboard")

            if cuota.estado == CuotaCredito.Estado.PAGADA:
                messages.info(request, "La cuota ya estaba pagada.")
                return redirect("contador_dashboard")

            cuota.estado = CuotaCredito.Estado.PAGADA
            cuota.save(update_fields=["estado"])

            cuenta = cuota.cuenta
            nuevo_saldo_usado = cuenta.saldo_usado - cuota.monto
            cuenta.saldo_usado = nuevo_saldo_usado if nuevo_saldo_usado > 0 else 0
            cuenta.save(update_fields=["saldo_usado"])
            messages.success(request, f"Cuota #{cuota.pk} marcada como pagada.")
            return redirect("contador_dashboard")

        if accion == "marcar_vencida":
            if cuota.estado == CuotaCredito.Estado.PAGADA:
                messages.error(request, "No puedes marcar vencida una cuota pagada.")
                return redirect("contador_dashboard")

            cuota.estado = CuotaCredito.Estado.VENCIDA
            cuota.save(update_fields=["estado"])
            messages.success(request, f"Cuota #{cuota.pk} marcada como vencida.")
            return redirect("contador_dashboard")

        messages.error(request, "Accion no valida.")
        return redirect("contador_dashboard")

    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    fecha_desde_raw = (request.GET.get("fecha_desde") or "").strip()
    fecha_hasta_raw = (request.GET.get("fecha_hasta") or "").strip()
    estado_pedido = (request.GET.get("estado_pedido") or "").strip()
    estado_cuota = (request.GET.get("estado_cuota") or "").strip()

    fecha_desde = None
    fecha_hasta = None

    if fecha_desde_raw:
        try:
            fecha_desde = date.fromisoformat(fecha_desde_raw)
        except ValueError:
            messages.warning(request, "Fecha desde invalida. Se ignoro el filtro.")

    if fecha_hasta_raw:
        try:
            fecha_hasta = date.fromisoformat(fecha_hasta_raw)
        except ValueError:
            messages.warning(request, "Fecha hasta invalida. Se ignoro el filtro.")

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        messages.warning(request, "Rango de fechas invalido: fecha desde es mayor que fecha hasta.")
        fecha_desde = None
        fecha_hasta = None

    pedidos_qs = Pedido.objects.select_related("usuario")
    if fecha_desde:
        pedidos_qs = pedidos_qs.filter(creado_en__date__gte=fecha_desde)
    if fecha_hasta:
        pedidos_qs = pedidos_qs.filter(creado_en__date__lte=fecha_hasta)
    if estado_pedido:
        pedidos_qs = pedidos_qs.filter(estado=estado_pedido)

    pedidos_mes_qs = pedidos_qs.filter(creado_en__date__gte=inicio_mes, creado_en__date__lte=hoy)

    total_ventas_expr = Case(
        When(total_final__gt=0, then=F("total_final")),
        default=F("total"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    total_pedidos = pedidos_qs.count()
    total_ventas = pedidos_qs.aggregate(total=Sum(total_ventas_expr)).get("total") or 0
    ventas_mes = pedidos_mes_qs.aggregate(total=Sum(total_ventas_expr)).get("total") or 0
    pedidos_mes = pedidos_mes_qs.count()

    cuentas_qs = CuentaCredito.objects.select_related("maestro", "maestro__usuario")
    total_credito_usado = cuentas_qs.aggregate(total=Sum("saldo_usado")).get("total") or 0
    total_cupo_aprobado = cuentas_qs.aggregate(total=Sum("cupo_aprobado")).get("total") or 0
    cuentas_credito_activas = cuentas_qs.filter(estado=CuentaCredito.Estado.ACTIVA).count()

    cuotas_qs = CuotaCredito.objects.select_related(
        "cuenta",
        "cuenta__maestro",
        "cuenta__maestro__usuario",
    )
    if estado_cuota:
        cuotas_qs = cuotas_qs.filter(estado=estado_cuota)
    else:
        cuotas_qs = cuotas_qs.filter(
            Q(estado=CuotaCredito.Estado.PENDIENTE) | Q(estado=CuotaCredito.Estado.VENCIDA)
        )

    if fecha_desde:
        cuotas_qs = cuotas_qs.filter(fecha_vencimiento__gte=fecha_desde)
    if fecha_hasta:
        cuotas_qs = cuotas_qs.filter(fecha_vencimiento__lte=fecha_hasta)

    cuotas_pendientes_vencidas_qs = cuotas_qs
    total_deuda_credito = cuotas_pendientes_vencidas_qs.aggregate(total=Sum("monto")).get("total") or 0

    cuotas_vencidas_qs = cuotas_pendientes_vencidas_qs.filter(
        Q(estado=CuotaCredito.Estado.VENCIDA)
        | Q(estado=CuotaCredito.Estado.PENDIENTE, fecha_vencimiento__lt=hoy)
    )
    cuotas_vencidas = cuotas_vencidas_qs.count()
    monto_vencido = cuotas_vencidas_qs.aggregate(total=Sum("monto")).get("total") or 0

    ultimos_pedidos = list(pedidos_qs.order_by("-creado_en")[:10])
    cuotas_recientes = list(
        cuotas_pendientes_vencidas_qs.order_by("-fecha_vencimiento", "-creado_en")[:10]
    )

    export = (request.GET.get("export") or "").strip()
    if export == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_pedidos_contador.csv"'
        writer = csv.writer(response)
        writer.writerow(["pedido_id", "cliente", "estado", "total", "fecha"])

        for pedido in pedidos_qs.order_by("-creado_en"):
            total_pedido = pedido.total_final if pedido.total_final and pedido.total_final > 0 else pedido.total
            writer.writerow([
                pedido.pk,
                getattr(pedido.usuario, "email", ""),
                pedido.estado,
                total_pedido,
                pedido.creado_en.isoformat(),
            ])
        return response

    if export == "cuotas_csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_cuotas_contador.csv"'
        writer = csv.writer(response)
        writer.writerow(["cuota_id", "maestro_pyme", "monto", "fecha_vencimiento", "estado"])

        for cuota in cuotas_pendientes_vencidas_qs.order_by("-fecha_vencimiento", "-creado_en"):
            writer.writerow([
                cuota.pk,
                getattr(cuota.cuenta.maestro.usuario, "email", ""),
                cuota.monto,
                cuota.fecha_vencimiento.isoformat(),
                cuota.estado,
            ])
        return response

    return render(
        request,
        "dashboard/contador.html",
        {
            "total_pedidos": total_pedidos,
            "total_ventas": total_ventas,
            "ventas_mes": ventas_mes,
            "pedidos_mes": pedidos_mes,
            "total_credito_usado": total_credito_usado,
            "total_cupo_aprobado": total_cupo_aprobado,
            "total_deuda_credito": total_deuda_credito,
            "cuotas_vencidas": cuotas_vencidas,
            "monto_vencido": monto_vencido,
            "cuentas_credito_activas": cuentas_credito_activas,
            "ultimos_pedidos": ultimos_pedidos,
            "cuotas_recientes": cuotas_recientes,
            "filtros": {
                "fecha_desde": fecha_desde_raw,
                "fecha_hasta": fecha_hasta_raw,
                "estado_pedido": estado_pedido,
                "estado_cuota": estado_cuota,
            },
            "estados_pedido": Pedido.Estado.choices,
            "estados_cuota": CuotaCredito.Estado.choices,
            "hoy": hoy,
            "soporta_estado_pagada": hasattr(CuotaCredito.Estado, "PAGADA"),
        },
    )


def _requiere_vendedor(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in [Usuario.Rol.VENDEDOR, Usuario.Rol.ADMIN]:
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
        return view_func(request, *args, **kwargs)

    return wrapper


@_requiere_vendedor
def vendedor_dashboard_operativo_view(request):
    Pedido = apps.get_model("pedidos", "Pedido")

    total_ventas_expr = Case(
        When(total_final__gt=0, then=F("total_final")),
        default=F("total"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    pedidos_generados_qs = (
        Pedido.objects.select_related("usuario")
        .prefetch_related(
            "items__producto",
            "items__solicitud_asesoria",
            "items__solicitud_asesoria__servicio",
        )
        .filter(estado=Pedido.Estado.GENERADO)
        .order_by("-creado_en")
    )
    pedidos_aprobados_qs = (
        Pedido.objects.select_related("usuario")
        .filter(estado=Pedido.Estado.APROBADO)
        .order_by("-creado_en")
    )

    soporta_rechazado = hasattr(Pedido.Estado, "RECHAZADO")
    pedidos_rechazados_qs = Pedido.objects.none()
    if soporta_rechazado:
        pedidos_rechazados_qs = (
            Pedido.objects.select_related("usuario")
            .filter(estado=Pedido.Estado.RECHAZADO)
            .order_by("-creado_en")
        )

    estados_relevantes = [Pedido.Estado.GENERADO, Pedido.Estado.APROBADO]
    if soporta_rechazado:
        estados_relevantes.append(Pedido.Estado.RECHAZADO)

    pedidos_relevantes_qs = Pedido.objects.select_related("usuario").filter(
        estado__in=estados_relevantes
    )

    total_ventas_aprobadas = (
        pedidos_aprobados_qs.aggregate(total=Sum(total_ventas_expr)).get("total") or 0
    )

    return render(
        request,
        "dashboard/vendedor.html",
        {
            "pedidos_generados": pedidos_generados_qs,
            "pedidos_aprobados": pedidos_aprobados_qs,
            "pedidos_rechazados": pedidos_rechazados_qs,
            "total_generados": pedidos_generados_qs.count(),
            "total_aprobados": pedidos_aprobados_qs.count(),
            "total_rechazados": pedidos_rechazados_qs.count() if soporta_rechazado else None,
            "total_ventas_aprobadas": total_ventas_aprobadas,
            "pedidos_recientes": pedidos_relevantes_qs.order_by("-creado_en")[:10],
            "soporta_rechazado": soporta_rechazado,
        },
    )


def _aplicar_parche_vendedor_dashboard():
    """Enruta el callback de vendedor al dashboard operativo definido en esta app."""
    try:
        from apps.pedidos import views as pedidos_views

        pedidos_views.vendedor_dashboard_view = vendedor_dashboard_operativo_view
    except Exception:
        # No interrumpe el arranque si el modulo no esta disponible en este contexto.
        pass


_aplicar_parche_vendedor_dashboard()

