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
from apps.credito import services as credito_services
from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro
from apps.pagos import services as pagos_services

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
    productos_destacados = catalogo_services.obtener_productos_activos()[:12]
    servicios_maestro_destacados = (
        ServicioMaestro.objects.filter(
            activo=True,
            maestro__estado=PerfilMaestroPyme.Estado.APROBADO,
        )
        .select_related("maestro", "maestro__usuario")
        .order_by("-creado_en")[:9]
    )
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
            "servicios_maestro_destacados": servicios_maestro_destacados,
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
    from .admin_views import admin_dashboard_view as _admin_dashboard_view

    return _admin_dashboard_view(request)


@_requiere_admin
def admin_usuarios_dashboard_view(request):
    from .admin_views import admin_usuarios_dashboard_view as _admin_usuarios_dashboard_view

    return _admin_usuarios_dashboard_view(request)


@_requiere_admin
def crear_usuario_interno_view(request):
    from .admin_views import crear_usuario_interno_view as _crear_usuario_interno_view

    return _crear_usuario_interno_view(request)


@_requiere_admin
def editar_usuario_interno_view(request, pk):
    from .admin_views import editar_usuario_interno_view as _editar_usuario_interno_view

    return _editar_usuario_interno_view(request, pk)


@_requiere_admin
def cambiar_estado_usuario_view(request, pk):
    from .admin_views import cambiar_estado_usuario_view as _cambiar_estado_usuario_view

    return _cambiar_estado_usuario_view(request, pk)


@_requiere_contador
def contador_dashboard_view(request):
    Pedido = apps.get_model("pedidos", "Pedido")
    CuotaCredito = apps.get_model("credito", "CuotaCredito")

    if request.method == "POST":
        accion = (request.POST.get("accion") or "").strip()
        cuota_id = request.POST.get("cuota_id")
        try:
            if accion == "marcar_pagada":
                cuota = credito_services.marcar_cuota_pagada(cuota_id)
                if cuota.estado == CuotaCredito.Estado.PAGADA:
                    messages.success(request, f"Cuota #{cuota.pk} marcada como pagada.")
            elif accion == "marcar_vencida":
                cuota = credito_services.marcar_cuota_vencida(cuota_id)
                messages.success(request, f"Cuota #{cuota.pk} marcada como vencida.")
            else:
                messages.error(request, "Accion no valida.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("contador_dashboard")

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

    resumen_pagos = pagos_services.obtener_resumen_contador_pagos(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        payment_status=estado_pedido,
    )
    datos_credito = credito_services.obtener_datos_contador_credito(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        estado_cuota=estado_cuota,
    )
    pagos_webpay_qs = pagos_services.obtener_pagos_webpay(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    pagos_ferrecredito_qs = pagos_services.obtener_pagos_ferrecredito(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    pagos_tienda_pendientes_qs = pagos_services.obtener_pagos_tienda_pendientes(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    export = (request.GET.get("export") or "").strip()
    if export == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_pedidos_contador.csv"'
        writer = csv.writer(response)
        writer.writerow(["pedido_id", "cliente", "estado_operativo", "payment_status", "total", "fecha"])

        for pedido in resumen_pagos["pedidos_qs"].order_by("-creado_en"):
            total_pedido = pedido.total_final if pedido.total_final and pedido.total_final > 0 else pedido.total
            writer.writerow([
                pedido.pk,
                getattr(pedido.usuario, "email", ""),
                pedido.estado,
                pedido.payment_status,
                total_pedido,
                pedido.creado_en.isoformat(),
            ])
        return response

    if export == "cuotas_csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_cuotas_contador.csv"'
        writer = csv.writer(response)
        writer.writerow(["cuota_id", "maestro_pyme", "monto", "fecha_vencimiento", "estado"])

        for cuota in datos_credito["cuotas_qs"].order_by("-fecha_vencimiento", "-creado_en"):
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
            "total_pedidos": resumen_pagos["total_pedidos"],
            "total_ventas": resumen_pagos["total_ventas"],
            "ventas_mes": resumen_pagos["ventas_mes"],
            "pedidos_mes": resumen_pagos["pedidos_mes"],
            "total_credito_usado": datos_credito["total_credito_usado"],
            "total_cupo_aprobado": datos_credito["total_cupo_aprobado"],
            "total_deuda_credito": datos_credito["total_deuda_credito"],
            "cuotas_vencidas": datos_credito["cuotas_vencidas"],
            "monto_vencido": datos_credito["monto_vencido"],
            "cuentas_credito_activas": datos_credito["cuentas_credito_activas"],
            "ultimos_pedidos": resumen_pagos["ultimos_pedidos"],
            "cuotas_recientes": datos_credito["cuotas_recientes"],
            "pagos_webpay": list(pagos_webpay_qs.order_by("-creado_en")[:10]),
            "pagos_ferrecredito": list(pagos_ferrecredito_qs.order_by("-creado_en")[:10]),
            "pagos_tienda_pendientes": list(pagos_tienda_pendientes_qs.order_by("-creado_en")[:10]),
            "filtros": {
                "fecha_desde": fecha_desde_raw,
                "fecha_hasta": fecha_hasta_raw,
                "estado_pedido": estado_pedido,
                "estado_cuota": estado_cuota,
            },
            "estados_pedido": Pedido.PaymentStatus.choices,
            "estados_cuota": CuotaCredito.Estado.choices,
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


def _requiere_bodeguero(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in [Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN]:
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
        return view_func(request, *args, **kwargs)

    return wrapper


@_requiere_bodeguero
def bodeguero_dashboard_operativo_view(request):
    Pedido = apps.get_model("pedidos", "Pedido")

    pedidos_aprobados = (
        Pedido.objects.select_related("usuario")
        .prefetch_related(
            "items__producto",
            "items__solicitud_asesoria",
            "items__solicitud_asesoria__servicio",
        )
        .filter(estado=Pedido.Estado.APROBADO)
        .order_by("-creado_en")
    )
    pedidos_en_preparacion = (
        Pedido.objects.select_related("usuario")
        .prefetch_related(
            "items__producto",
            "items__solicitud_asesoria",
            "items__solicitud_asesoria__servicio",
        )
        .filter(estado=Pedido.Estado.EN_PREPARACION)
        .order_by("-creado_en")
    )

    estados_listos = [Pedido.Estado.LISTO]
    if hasattr(Pedido.Estado, "ENTREGADO"):
        estados_listos.append(Pedido.Estado.ENTREGADO)

    pedidos_listos = (
        Pedido.objects.select_related("usuario")
        .filter(estado__in=estados_listos)
        .order_by("-creado_en")
    )

    estados_bodega = [Pedido.Estado.APROBADO, Pedido.Estado.EN_PREPARACION, Pedido.Estado.LISTO]
    if hasattr(Pedido.Estado, "ENTREGADO"):
        estados_bodega.append(Pedido.Estado.ENTREGADO)

    pedidos_recientes_bodega = (
        Pedido.objects.select_related("usuario")
        .filter(estado__in=estados_bodega)
        .order_by("-creado_en")[:10]
    )

    total_aprobados = pedidos_aprobados.count()
    total_en_preparacion = pedidos_en_preparacion.count()
    total_listos = pedidos_listos.count()

    return render(
        request,
        "dashboard/bodeguero.html",
        {
            "pedidos_aprobados": pedidos_aprobados,
            "pedidos_en_preparacion": pedidos_en_preparacion,
            "pedidos_listos": pedidos_listos,
            "total_aprobados": total_aprobados,
            "total_en_preparacion": total_en_preparacion,
            "total_listos": total_listos,
            "total_pedidos_bodega": total_aprobados + total_en_preparacion + total_listos,
            "pedidos_recientes_bodega": pedidos_recientes_bodega,
            "estado_preparacion": Pedido.Estado.EN_PREPARACION,
            "estado_listo": Pedido.Estado.LISTO,
            "estado_entregado": Pedido.Estado.ENTREGADO if hasattr(Pedido.Estado, "ENTREGADO") else None,
        },
    )


def _aplicar_parche_bodeguero_dashboard():
    """Enruta el callback de bodeguero al dashboard operativo definido en esta app."""
    try:
        from apps.pedidos import views as pedidos_views

        pedidos_views.bodeguero_dashboard_view = bodeguero_dashboard_operativo_view
    except Exception:
        # No interrumpe el arranque si el modulo no esta disponible en este contexto.
        pass


_aplicar_parche_bodeguero_dashboard()

