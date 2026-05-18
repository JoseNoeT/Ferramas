# Integraciones Externas FERREMAX / FERREMAS (ASY5131)

## A) Resumen ejecutivo
En el proyecto se integraron dos APIs externas con objetivos distintos y complementarios:

1. **Transbank Webpay Plus** (transaccional): habilita pago en linea con flujo real de autorizacion en ambiente de integracion/testing.
2. **mindicador.cl** (informativa): incorpora indicadores economicos oficiales para apoyo visual y contexto financiero.

Estas integraciones cumplen con **Integracion de Plataformas** porque conectan FERREMAS con servicios externos reales, traducen respuestas externas a logica interna controlada y exponen resultados mediante flujos de negocio y endpoints propios.

---

## B) API externa 1: Transbank Webpay Plus
### Objetivo
Permitir pago por tarjeta en checkout mediante una pasarela externa, con trazabilidad completa del estado de pago.

### Ambiente usado
- `integration/testing` de Transbank Webpay Plus.

### Flujo tecnico implementado
1. Usuario confirma checkout con medio de pago Webpay.
2. Sistema crea `Pedido`.
3. Sistema crea registro `Pago` en estado inicial.
4. Servicio ejecuta `Transaction.create`.
5. Cliente es redirigido a Webpay mediante **POST** con `token_ws`.
6. Webpay retorna a FERREMAS (`token_ws`).
7. Servicio ejecuta `Transaction.commit`.
8. Sistema actualiza estado de `Pago` y estado de pago de `Pedido`.

### Archivos principales involucrados
- [backend/apps/pagos/models.py](backend/apps/pagos/models.py)
- [backend/apps/pagos/services.py](backend/apps/pagos/services.py)
- [backend/apps/pagos/views.py](backend/apps/pagos/views.py)
- [backend/apps/pagos/urls.py](backend/apps/pagos/urls.py)
- [backend/apps/pedidos/models.py](backend/apps/pedidos/models.py)
- [backend/apps/pedidos/views.py](backend/apps/pedidos/views.py)
- [frontend/templates/pages/checkout.html](frontend/templates/pages/checkout.html)
- [frontend/templates/pages/confirmacion.html](frontend/templates/pages/confirmacion.html)
- [frontend/templates/pages/webpay_redirect.html](frontend/templates/pages/webpay_redirect.html)
- [backend/core/settings.py](backend/core/settings.py)

### Modelo `Pago`
Se implementa entidad de persistencia para trazabilidad del proceso Webpay.

Campos relevantes de defensa:
- `token_ws`
- `buy_order`
- `response_code`
- `authorization_code`
- `raw_response`
- `estado`

### Endpoint/rutas usadas
- Inicio: `/api/pagos/webpay/iniciar/<pedido_id>/`
- Retorno: `/api/pagos/webpay/retorno/`

### Evidencia de prueba
- Pedido: **#42**
- Resultado pago: **autorizado**
- Codigo de autorizacion: **1213**
- Commit asociado: **e9c4be6**

---

## C) API externa 2: mindicador.cl
### Objetivo
Consumir indicadores economicos externos para exponer informacion financiera de referencia en la plataforma.

### Endpoint externo consumido
- `https://mindicador.cl/api`

### Endpoint interno creado
- `GET /api/integraciones/indicadores/`

### Indicadores mostrados
- UF
- Dolar
- Euro
- UTM

### Uso visual
- Home publico.
- Dashboard contador.

### Nota funcional
**Valores informativos. No modifican precios ni pagos del sistema.**

Commit asociado: **b551567**.

---

## D) Tabla comparativa

| API externa | Tipo de integracion | Entrada | Proceso interno | Salida | Modulo afectado | Riesgo controlado |
|---|---|---|---|---|---|---|
| Transbank Webpay Plus | Transaccional (pago) | Pedido + monto + token_ws | create -> redireccion POST -> retorno -> commit -> persistencia estados | Pago autorizado/rechazado + confirmacion de pedido | pagos, pedidos, checkout, confirmacion | Sin datos sensibles de tarjeta; idempotencia y estados de pago separados |
| mindicador.cl | Informativa (consulta) | Solicitud GET a endpoint interno | Llamado HTTP externo con timeout + normalizacion de respuesta | JSON con uf/dolar/euro/utm + fecha + fuente | integraciones + componentes frontend | Degradacion controlada ante falla externa (respuesta sin romper vista) |

---

## E) Como demostrar en presentacion
1. Abrir Home y mostrar widget de indicadores economicos.
2. Mostrar respuesta del endpoint `GET /api/integraciones/indicadores/`.
3. Ir a checkout y seleccionar Webpay Plus.
4. Ejecutar flujo de pago en ambiente de testing hasta autorizacion.
5. Mostrar confirmacion del pedido y estado final de pago.

---

## F) Riesgos y controles
1. Webpay en ambiente testing no mueve dinero real.
2. No se almacenan datos sensibles de tarjeta en base de datos.
3. mindicador.cl puede fallar; la aplicacion degrada sin romper flujo principal.
4. Webpay mantiene estado de pago separado del estado logistico del pedido.
