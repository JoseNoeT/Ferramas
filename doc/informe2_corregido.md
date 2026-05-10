

FERREMAS | Evaluación Parcial 1
Integración de Plataformas - ASY5131

Informe Final Corregido y Reforzado
Análisis As Is, propuesta To Be, reglas Maestro PYME, FerreCrédito, fidelización e integración REST


Asignatura	Integración de Plataformas
Sigla	ASY5131
Institución	Duoc UC
Carrera	Ingeniería en Informática
Profesor	Juan Alberto Ghana
Estudiante	José Miguel Noe Torres
Fecha	Abril 2026
Stack objetivo	Django + Django REST Framework + PostgreSQL + JWT

Documento corregido incorporando los requerimientos adicionales de Maestro PYME, FerreCrédito, descuento de primera compra, publicación de servicios, encuesta virtual y sistema de puntos.
 
Tabla de contenido
1. Introducción
2. Objetivos del informe
3. Metodología de análisis
4. Contexto del negocio y problema detectado
5. Modelo de negocio actual de FERREMAS
6. Análisis del estado actual (As Is)
7. Propuesta de estado futuro (To Be)
8. Integración de plataformas y webservices
9. Modelo técnico de implementación en Django REST
10. Comparación As Is vs To Be
11. Matriz de cobertura de la pauta y requerimientos adicionales
12. Riesgos, controles e inconsistencias corregidas
13. Conclusiones
14. Referencias
 
1. Introducción
El presente informe desarrolla la etapa de análisis, planificación y normalización técnica del caso FERREMAS en el contexto de la asignatura Integración de Plataformas. Su propósito es estudiar el negocio, describir el estado actual de operación, proyectar un estado futuro orientado al comercio electrónico e identificar los puntos de integración que justifican el uso de webservices dentro de una arquitectura por capas.
Esta versión corrige y refuerza el informe anterior incorporando explícitamente los requerimientos adicionales solicitados para el módulo Maestro PYME, la cuenta corriente interna FerreCrédito, el descuento de primera compra, la publicación de servicios de maestros, el cobro fijo de confirmación de asesoría, el voucher de contacto, la notificación por correo, la encuesta virtual de satisfacción y el sistema de puntos acumulables.
El documento mantiene una línea lógica entre negocio, procesos, BPMN, capas afectadas, servicios REST y modelado backend en Django REST Framework. No se copia una implementación Java; se interpreta el negocio y se traduce a una solución propia, modular y defendible académicamente.
2. Objetivos del informe
2.1 Objetivo general
Analizar y planificar la situación actual y futura de FERREMAS mediante la identificación del modelo de negocio, el levantamiento del proceso operativo principal en su estado As Is, la propuesta de un modelo To Be orientado al comercio electrónico y la definición de integraciones mediante webservices, incorporando las reglas específicas de Maestro PYME, FerreCrédito, fidelización por puntos y postventa.
2.2 Objetivos específicos
•	Identificar el modelo de negocio, problema detectado, actores, procesos y roles involucrados.
•	Clasificar los procesos en operativos, de apoyo, de gestión y estratégicos.
•	Describir el estado actual del proceso principal, incluyendo flujo, entradas, salidas, recursos, sistemas y capas afectadas.
•	Definir el estado futuro con ecommerce, trazabilidad, despacho/retiro, pagos, fidelización, Maestro PYME y encuesta postventa.
•	Normalizar las reglas de negocio adicionales: primera compra con 30%, FerreCrédito, cupo, cuotas, deuda al día, servicios de maestros y notificaciones.
•	Definir webservices REST coherentes con la arquitectura por capas y con la responsabilidad del dato.
•	Dejar una base técnica implementable en Django REST Framework, separando modelos, services, serializers, ViewSets y permisos.
3. Metodología de análisis
La metodología aplicada se organiza en cuatro fases. Primero, se revisa el caso base para comprender el negocio y el problema central. Segundo, se analiza el documento de requerimientos adicionales para incorporar las funcionalidades de Maestro PYME, FerreCrédito, puntos y encuesta. Tercero, se normalizan los procesos As Is y To Be, separando lo documentado de lo inferido y de lo recomendado. Finalmente, se traduce el modelo de negocio a una arquitectura técnica en Django REST Framework.
Fase	Actividad	Resultado esperado
Fase 1 - Comprensión documental	Revisión del caso FERREMAS y requerimientos adicionales	Actores, procesos, reglas de negocio y debilidades identificadas
Fase 2 - Modelado técnico	Definición de módulos, entidades, estados, servicios REST y responsabilidades	Arquitectura backend coherente con el informe
Fase 3 - Validación	Comparación entre documentación, To Be y cobertura de RF	Faltantes detectados y corregidos
Fase 4 - Implementación futura	Preparación de estructura Django REST	Base lista para codificación modular

4. Contexto del negocio y problema detectado
FERREMAS es una distribuidora de productos de ferretería y construcción con presencia en la Región Metropolitana y en regiones, con proyección de expansión nacional. Comercializa herramientas manuales y eléctricas, pinturas, materiales eléctricos, accesorios y artículos de seguridad, trabajando con marcas reconocidas del sector.
La empresa opera mediante sucursales físicas con una estructura organizativa definida. Cada tienda cuenta con administrador, vendedor o encargado, bodeguero y contador, actores que participan en la venta, preparación de productos, control financiero y supervisión comercial.
El problema central es la ausencia de una plataforma de venta en línea. La dependencia del canal presencial redujo la continuidad operativa en escenarios de restricción física y limita la escalabilidad comercial. La actualización del caso agrega una dimensión social y económica: integrar a maestros y PYMES como clientes especiales y prestadores de servicios asociados a la construcción y mejora de viviendas.
Problema	Efecto en el negocio	Respuesta To Be
Dependencia de tienda física	Menor cobertura y baja continuidad operacional	Canal ecommerce integrado
Baja trazabilidad de pedidos	Cliente y áreas internas no visualizan estados con claridad	Estados digitales del pedido
Procesos manuales entre ventas, bodega y contabilidad	Demoras, duplicidad y riesgo de error	Servicios REST y paneles internos
Falta de integración con profesionales externos	Pérdida de oportunidad de valor agregado	Módulo Maestro PYME y servicios asociados
Clientes sin acceso a crédito bancario	Limitación para maestros/PYMES no bancarizados	FerreCrédito como cuenta corriente interna

5. Modelo de negocio actual de FERREMAS
El modelo actual se sostiene principalmente sobre la venta presencial de productos en sucursal. El valor entregado proviene de la disponibilidad de productos, variedad de marcas, asesoría comercial y entrega inmediata en tienda. El proceso principal es la venta presencial; a su alrededor operan inventario, facturación, control financiero, informes y estrategias de promoción.
5.1 Actores y roles
Actor	Rol principal	Responsabilidades en el estado actual
Administrador	Gestión y supervisión	Genera informes mensuales, revisa desempeño y define promociones o estrategias de venta.
Vendedor / Encargado	Atención comercial	Asesora al cliente, recibe el pedido, coordina con bodega y gestiona pago/facturación.
Bodeguero	Apoyo operativo e inventario	Consulta stock, organiza bodega, prepara productos y los entrega para la venta.
Contador	Control financiero	Registra transacciones, controla pagos, apoya validaciones financieras y elabora balances.
Cliente	Demandante del servicio	Solicita productos, recibe orientación, compra y recibe el bien adquirido.

5.2 Procesos identificados y clasificación
Proceso	Tipo	Objetivo	Justificación
Venta presencial de productos	Operativo	Concretar la venta	Genera directamente el producto/servicio que recibe el cliente.
Atención y asesoría comercial	Operativo	Orientar la compra	Forma parte del proceso que termina en la venta y satisfacción del cliente.
Gestión de inventario y preparación	Apoyo	Asegurar disponibilidad	Permite que la venta se concrete, pero no entrega valor final de forma aislada.
Facturación y registro financiero	Apoyo / gestión operativa	Formalizar y controlar la transacción	Hace posible la venta ordenada y deja trazabilidad financiera.
Informes de venta y desempeño	Gestión	Monitorear el proceso	Mide resultados y apoya el control del negocio.
Estrategias de venta y promociones	Estratégico	Orientar dirección comercial	Define mejoras, promociones y foco comercial.

5.3 Procesos clave involucrados en la integración
Proceso clave	Tipo	Objetivo	Sistemas / datos involucrados	Necesidad de integración
Gestión de venta y pedido	Operativo	Registrar y canalizar la compra	Catálogo, cliente, pedido, total de compra	Alta
Gestión de inventario y preparación	Apoyo operativo	Validar stock y preparar productos	Stock, ubicación, estado de preparación	Alta
Gestión de pago y facturación	Apoyo operativo	Confirmar pago y formalizar transacción	Monto, medio de pago, comprobante	Alta
Gestión de entrega y trazabilidad	Operativo / control	Despachar, retirar y cerrar pedido	Estado del pedido, entrega, confirmación	Alta
Gestión Maestro PYME y FerreCrédito	Operativo / comercial	Habilitar cliente especial, crédito interno y servicios asociados	Perfil maestro, cupo, deuda, servicios, notificaciones	Alta
Fidelización y postventa	Gestión / apoyo	Acumular puntos y levantar satisfacción	Puntos, movimientos, encuesta, pedido asociado	Media-Alta

5.4 Relación entre procesos y mapa general
Los procesos se relacionan de forma encadenada. El cliente solicita un producto, el vendedor orienta y registra el pedido, el bodeguero verifica disponibilidad y prepara productos, el contador registra la transacción y controla el pago, y el administrador supervisa resultados. En el To Be se agrega una segunda línea de valor: Maestros/PYMES se registran, compran como clientes, acceden a FerreCrédito y pueden publicar servicios que el cliente final puede contratar como asesoría inicial.
 
Fuente: elaboración propia.
6. Análisis del estado actual (As Is)
6.1 Descripción general del proceso actual
En el estado actual, el proceso principal se desarrolla mediante atención presencial. El flujo comienza cuando el cliente llega a la sucursal y solicita asesoría o un producto. El vendedor se convierte en el punto de contacto comercial y coordina con bodega y contabilidad.
El As Is es funcional, pero altamente dependiente de la presencialidad y de la coordinación secuencial entre áreas. La venta depende de validación de stock, cobro, facturación y registro financiero posterior.
6.2 Secuencia operativa del flujo actual
Paso	Actor responsable	Actividad actual
1	Cliente	Visita la tienda o solicita atención comercial.
2	Vendedor / Encargado	Asesora al cliente e identifica la necesidad de compra.
3	Vendedor / Encargado	Recibe y procesa el pedido.
4	Bodeguero	Verifica disponibilidad y prepara productos solicitados.
5	Vendedor / Encargado	Gestiona el pago y la facturación de la venta.
6	Contador	Registra la transacción y controla pagos.
7	Administrador	Supervisa resultados mediante informes y seguimiento del desempeño.

6.3 Entradas, salidas y recursos
Elemento	Descripción
Entrada que activa el proceso	Solicitud de compra del cliente.
Información requerida	Producto solicitado, precio, disponibilidad de stock, medio de pago y datos para facturación.
Recursos utilizados	Personal de tienda, bodega, caja o punto de venta, sistemas internos de apoyo y registros administrativos/contables.
Salida del proceso	Venta concretada y registrada.
Resultado para el cliente	Producto entregado y comprobante de compra.
Registros generados	Registro de venta, boleta o factura, registro contable y datos para reportes de control.

6.4 Sistemas y capas del As Is
Sistema / componente	Responsable principal	Uso en el As Is
Sistema de ventas en sucursal	Vendedor	Registrar pedido, consultar precio, calcular venta y gestionar cobro.
Módulo de inventario / bodega	Bodeguero	Consultar stock, organizar inventario y preparar productos.
Sistema de facturación / caja	Vendedor / caja	Emitir comprobante y dejar constancia del pago.
Sistema contable / financiero	Contador	Registrar transacciones, controlar pagos y elaborar balances.
Módulo administrativo de reportes	Administrador	Generar informes y revisar desempeño general.
Comunicación operativa manual	Áreas internas	Coordinar traspasos de información entre vendedor, bodega y contabilidad.

Capa	Qué ocurre en FERREMAS As Is	Impacto del problema actual
Presentación	Atención presencial, captura del pedido y terminales internas.	Muy alto: no existe canal digital para el cliente.
Negocio	Validación de stock, procesamiento del pedido, cálculo del total y cierre de venta.	Alto: lógica centrada en presencialidad.
Datos	Catálogo, inventario, ventas, pagos, boletas/facturas, registros contables y reportes.	Medio-Alto: no existe flujo digital integrado de pedidos y estados.

6.5 Debilidades del estado actual
•	Tareas manuales repetidas en atención, consulta de stock, coordinación con bodega, facturación y registro financiero.
•	Dependencia del canal presencial para concretar ventas.
•	Baja visibilidad del estado del pedido para cliente y áreas internas.
•	Ausencia de flujo digital integrado para catálogo, pedido, pago, entrega y postventa.
•	Inexistencia de gestión digital de puntos, encuesta postventa, Maestro PYME, FerreCrédito y servicios asociados.
•	No existe control automático de cupo, deuda al día ni validación de segunda compra para clientes Maestro/PYME.
6.6 Espacios para diagramas As Is
 
Figura 2. BPMN As Is del proceso operativo principal de venta presencial.
 
Figura 3. BPMN As Is del proceso de gestión de inventario y preparación.
 
Figura 4. BPMN As Is del proceso de facturación, registro y control financiero.
7. Propuesta de estado futuro (To Be)
7.1 Objetivo de mejora
El To Be busca resolver la dependencia de venta presencial, falta de canal digital, baja visibilidad del pedido y coordinación manual entre áreas. El nuevo proceso permite operar de forma híbrida, incorporando ecommerce, actualización automática de inventario, fidelización por puntos, beneficios para Maestro PYME, FerreCrédito, servicios asociados y encuesta de satisfacción.
7.2 Rediseño del proceso
El proceso inicia en el sitio web, cuando el cliente navega por catálogo, inicia sesión o se registra y genera un pedido. Se mantienen actividades clave como validación de stock, preparación en bodega, control de pagos, registro contable y supervisión administrativa, pero se digitalizan y trazan mediante estados.
•	El cliente normal puede comprar productos, usar puntos, elegir retiro/despacho y responder encuesta postventa.
•	El Maestro/PYME se registra en una vista especializada, compra como cliente normal y puede publicar servicios/productos asociados.
•	Solo Maestro/PYME puede pagar usando FerreCrédito, sujeto a cupo, deuda al día y aprobación administrativa.
•	La primera compra de Maestro/PYME aplica 30% de descuento sobre el total de facturación.
•	Los servicios de maestros pueden agregarse como asesoría adicional con cobro fijo de confirmación de $5.000.
•	El pago final del servicio profesional se realiza entre cliente final y Maestro/PYME, fuera de los sistemas de FERREMAS.
7.3 Actores del To Be
Actor	Responsabilidad en el To Be
Cliente web	Navega por catálogo, registra pedido, elige entrega, paga, usa puntos, consulta estado y responde encuesta.
Cliente Maestro/PYME	Funciona como cliente normal, accede a vista especializada, descuento primera compra y FerreCrédito.
Maestro/PYME prestador	Publica productos/servicios, recibe notificación con datos del cliente y contacta externamente.
Vendedor	Aprueba o rechaza pedidos, organiza despacho y da seguimiento operativo.
Bodeguero	Recibe órdenes digitales, prepara productos y actualiza estado.
Contador	Confirma transferencias, registra pagos, controla facturación y apoya revisión de FerreCrédito.
Administrador	Gestiona usuarios, cupos de crédito, incremento/disminución de cupo, reportes y operación digital.
Sistema web / ecommerce	Canaliza pedidos, muestra catálogo, registra estados, aplica puntos/descuentos y comunica áreas.
Pasarela o sistema externo de pago	Autoriza o confirma pagos electrónicos no asociados a FerreCrédito.
Servicio de correo/notificación	Envía voucher y correo mixto cliente-maestro cuando se compra asesoría.

7.4 Experiencia del cliente
En el estado futuro, el cliente puede comprar en línea, revisar catálogo, utilizar carrito de compras, seleccionar retiro o despacho, pagar electrónicamente, consultar estado del pedido, acumular y utilizar puntos, y responder encuesta de satisfacción. Además, puede contratar una asesoría inicial de Maestro/PYME como ítem adicional de confirmación.
Para Maestro/PYME, la experiencia agrega una vista diferenciada, registro especial, publicación de servicios, primera compra con descuento, pago con FerreCrédito y gestión de beneficios comerciales asociados a su perfil.
7.5 Módulo Maestro PYME y FerreCrédito
El módulo Maestro PYME no debe tratarse solo como una recomendación de servicios. Debe modelarse como un subdominio funcional compuesto por perfil especial, vista de registro, condición comercial, servicios publicados y cuenta corriente interna FerreCrédito.
Componente	Regla funcional	Responsable / dueño del dato
Vista Maestro/PYME	Permite registro diferenciado y acceso a beneficios especiales.	Sistema ecommerce / usuarios
Perfil Maestro/PYME	Extiende al cliente normal con datos de oficio, rubro, empresa y condición comercial.	Usuarios / Maestro PYME
Descuento primera compra	30% sobre el total de facturación, una sola vez por Maestro/PYME registrado.	Pedidos / promociones
FerreCrédito	Cuenta corriente interna exclusiva para Maestro/PYME.	Crédito / administración
Cupo máximo aprobado	El administrador valida, incrementa y gestiona el cupo disponible.	Administrador
Cuotas mensuales	Las compras a crédito pueden pactarse en cuotas cobradas mensualmente.	Crédito / contabilidad
Segunda compra	Solo se permite si el crédito actual está al día y no supera el cupo aprobado.	Servicio de crédito
Servicios publicados	Maestro/PYME puede publicar productos o servicios visibles en página principal.	Maestro PYME
Asesoría confirmada	Cliente paga $5.000 como confirmación de contacto.	Pedidos / pagos
Contacto externo	El cobro final del servicio ocurre entre cliente y maestro, fuera de FERREMAS.	Cliente final y Maestro/PYME

7.6 Reglas de negocio corregidas
Código	Regla de negocio	Validación técnica
RN-01	Todo Maestro/PYME debe registrarse antes de acceder a beneficios.	Perfil maestro_pyme activo asociado a usuario.
RN-02	El Maestro/PYME funciona como cliente normal para compras estándar.	Puede crear carrito, pedido y usar flujo general.
RN-03	Solo Maestro/PYME puede usar FerreCrédito.	Permiso por rol/tipo_cliente antes de seleccionar medio de pago.
RN-04	Primera compra Maestro/PYME aplica 30% de descuento total.	Validar que no exista compra previa cerrada con perfil Maestro/PYME.
RN-05	FerreCrédito permite comprar a crédito en cuotas mensuales.	Crear compra_credito y plan_cuotas.
RN-06	Para segunda compra debe estar al día.	Bloquear si existen cuotas vencidas o deuda morosa.
RN-07	No se puede superar cupo máximo aprobado.	total_credito_actual + nueva_compra <= cupo_aprobado.
RN-08	El administrador gestiona cupo y estado del crédito.	Endpoint protegido por rol administrador.
RN-09	El servicio de Maestro/PYME se agrega como ítem adicional de $5.000.	Crear línea de pedido tipo asesoría_confirmacion.
RN-10	El voucher debe incluir datos de contacto del Maestro/PYME.	Generar detalle en voucher asociado al pedido.
RN-11	Debe enviarse correo mixto a cliente y maestro.	Servicio de notificación post-confirmación.
RN-12	El pago final del servicio profesional no pasa por FERREMAS.	Registrar solo confirmación/contacto; no registrar cobro final externo.
RN-13	Los puntos se acumulan por compra y pueden usarse parcialmente.	CuentaPuntos + MovimientoPuntos.
RN-14	Si se usan puntos, solo se descuentan los puntos aplicados y se mantiene remanente.	Validación de saldo y transacción atómica.
RN-15	La encuesta se habilita después de entrega/cierre.	Pedido en estado entregado o cerrado.

7.7 Capas afectadas y relación con sistemas existentes
Aspecto	As Is	To Be
Canal principal	Atención presencial	Canal híbrido: tienda + ecommerce
Consulta de productos	Presencial o interna	Catálogo en línea y consulta interna
Gestión del pedido	Secuencial y manual	Registrada digitalmente y visible por estado
Coordinación entre áreas	Principalmente manual	Apoyada por servicios y estados digitales
Fidelización	No existe esquema digital de puntos	Puntos acumulables y descuentos por puntos
Servicios complementarios	No hay derivación digital	Servicios Maestro/PYME con confirmación de $5.000
Segmento Maestro PYME	Sin tratamiento digital diferenciado	Vista, registro, descuento, FerreCrédito y publicación de servicios
Postventa	Sin encuesta estructurada	Encuesta de satisfacción postventa
Inventario tras pago	Actualización no completamente automática	Actualización automática vía webservices
Crédito interno	No existe	FerreCrédito gestionado por administrador

7.8 Control y trazabilidad
El To Be debe hacer visibles los estados del proceso para todos los actores relevantes. La trazabilidad incluye creación de pedido, validación de stock, aplicación de puntos/descuentos, confirmación de pago o crédito, preparación, entrega, cierre, encuesta y eventos Maestro/PYME.
Grupo	Estados / eventos mínimos
Pedido	pedido_creado, stock_validado, pedido_aprobado, pedido_rechazado, en_preparacion, listo_para_retiro, en_despacho, entregado, cerrado
Pago	pago_pendiente, pago_confirmado, pago_rechazado, pago_en_validacion_manual
FerreCrédito	credito_solicitado, credito_aprobado, credito_bloqueado, cuota_pendiente, cuota_pagada, cuota_vencida, cliente_al_dia
Puntos	puntos_acumulados, puntos_usados, saldo_actualizado
Maestro/PYME	perfil_pendiente, perfil_aprobado, servicio_publicado, asesoria_confirmada, correo_enviado
Postventa	encuesta_habilitada, encuesta_respondida

7.9 Espacios para diagramas To Be
 
Figura 5. Mapa general de procesos de FERREMAS (To Be).
 
Figura 6. BPMN To Be del proceso operativo principal de venta integrada con ecommerce.
 
Figura 7. BPMN To Be del proceso de preparación, despacho/retiro y cierre del pedido.
8. Integración de plataformas y webservices
8.1 Necesidad real de integración
La consulta de stock en tiempo real, creación del pedido, actualización de estados, confirmación de pagos y trazabilidad no funcionan correctamente sin integración. A esto se suman puntos, FerreCrédito, publicación de servicios Maestro/PYME, notificación por correo y encuesta virtual.
La integración se justifica cuando un sistema requiere datos que pertenecen a otro. Los sistemas mínimos a conectar son ecommerce, inventario/bodega, pedidos, pagos, contabilidad, fidelización, Maestro PYME, crédito interno, notificaciones, vouchers y postventa.
8.2 Objetos de negocio y datos que viajan
Objeto / dato	Dato que viaja	Sistema dueño	Sistema que consulta	Sistema que actualiza
Producto	id, nombre, precio, categoría	Catálogo	Ecommerce / paneles	Catálogo
Stock	idProducto, stock, sucursal	Inventario	Ecommerce / vendedor	Inventario
Pedido	id, detalle, total, cliente, estado	Pedidos	Paneles internos	Pedidos
Pago	monto, medio, confirmación, referencia	Pasarela / contabilidad	Ecommerce / contador	Pasarela / contabilidad
FerreCrédito	cupo, saldo, deuda, cuotas, estado	Crédito interno	Ecommerce / admin / contador	Administrador / crédito
Puntos	saldo, ganados, usados, remanente	Fidelización	Ecommerce / cliente	Fidelización
Maestro/PYME	perfil, rubro, servicios, disponibilidad	Maestro PYME	Ecommerce / cliente	Maestro PYME
Servicio asociado	idServicio, precio_confirmación, maestro, datos_contacto	Maestro PYME / pedidos	Cliente / voucher	Pedidos / notificaciones
Encuesta	puntaje, comentario, pedido_asociado	Postventa	Admin / calidad	Postventa
Voucher	pedido, productos, pago, contacto maestro	Pedidos / voucher	Cliente / maestro	Voucher

8.3 Propuesta y ubicación de webservices
Webservice	Qué expone	Aplicación que expone	Aplicación que consume	Capa principal
WS_Productos	Consulta de catálogo y detalle de productos	Catálogo / ventas	Ecommerce	Negocio
WS_Stock	Disponibilidad por producto/sucursal y ajuste posterior al pago	Inventario / bodega	Ecommerce / vendedor	Negocio + datos
WS_Pedidos	Registro, detalle y actualización de pedidos	Pedidos	Paneles internos	Negocio
WS_Pagos	Confirmación y estado del pago	Pagos / pasarela / contabilidad	Ecommerce / contador	Negocio
WS_EstadosPedido	Seguimiento y cambio de estado	Módulo de estados	Cliente / vendedor / bodeguero	Negocio
WS_Entrega	Confirmación de despacho, retiro y cierre	Bodega / logística	Ecommerce / contador	Negocio
WS_Puntos	Consulta, acumulación y uso de puntos	Fidelización	Ecommerce / panel comercial	Negocio
WS_FerreCredito	Cupo, saldo, cuotas, validación de deuda al día	Crédito interno	Ecommerce / administrador / contador	Negocio
WS_MaestroPYME	Perfiles, servicios publicados y beneficios	Maestro PYME	Ecommerce / administración	Negocio
WS_ServicioMaestro	Compra de asesoría de $5.000 y datos de contacto	Maestro PYME / pedidos	Ecommerce / voucher	Negocio
WS_Notificaciones	Correo mixto cliente-maestro y avisos operativos	Notificaciones	Pedidos / Maestro PYME	Integración
WS_Voucher	Emisión de comprobante con detalle de maestro	Voucher / pedidos	Cliente / maestro / contabilidad	Negocio
WS_EncuestaSatisfaccion	Registro y consulta de evaluación postventa	Postventa / calidad	Ecommerce / administración	Negocio

8.4 Servicios específicos agregados por la actualización
Servicio	Endpoint REST sugerido	Regla cubierta
Registro Maestro/PYME	POST /api/maestros-pyme/registro/	RF vista y registro diferenciado
Validación FerreCrédito	POST /api/credito/validar-compra/	Solo Maestro/PYME, deuda al día y cupo suficiente
Gestión de cupo	PATCH /api/credito/cuentas/{id}/cupo/	Administrador valida, incrementa y gestiona cupo
Plan de cuotas	POST /api/credito/compras/{id}/cuotas/	Compra a crédito pactada en cuotas mensuales
Descuento primera compra	POST /api/pedidos/{id}/aplicar-descuento-maestro/	30% solo en primera compra
Servicio Maestro/PYME	POST /api/servicios-maestro/{id}/contratar/	Agrega asesoría de $5.000 al pedido
Correo mixto	POST /api/notificaciones/contacto-maestro/	Envía datos a cliente y maestro
Voucher con maestro	GET /api/pedidos/{id}/voucher/	Incluye detalle de contacto posterior
Puntos	POST /api/puntos/aplicar/	Descuenta puntos usados y conserva remanente
Encuesta	POST /api/encuestas/	Registra satisfacción postventa

8.5 Relación con REST, seguridad e interacción entre servicios
Los servicios se entienden como recursos de negocio. El ecommerce y los paneles internos consumen endpoints REST según el dominio responsable del dato. Las operaciones de consulta pueden usar caché; las operaciones de pago, crédito, puntos, cambio de estado, encuestas y notificaciones requieren consistencia transaccional y control de permisos.
Riesgo	Control técnico recomendado
Uso indebido de FerreCrédito por cliente normal	Permiso por rol y validación de tipo_cliente en service.
Superar cupo aprobado	Validación atómica antes de crear compra a crédito.
Compra con deuda vencida	Consulta de cuotas vencidas antes de autorizar segunda compra.
Aplicación repetida del 30%	Flag primera_compra_descuento_usado o consulta de compras cerradas.
Uso incorrecto de puntos	Bloqueo transaccional de saldo y movimientos de puntos.
Exponer datos de cliente al maestro sin compra confirmada	Enviar correo solo cuando pedido/asesoría esté confirmada.
Registrar como ingreso de Ferremas el servicio final maestro	Distinguir cargo_confirmacion_asesoria de pago_final_externo.

8.6 Espacios para diagramas de arquitectura y servicios
 
Figura 8. Diagrama de arquitectura por capas con ubicación de webservices.
 
Figura 9. Mapa de servicios REST e interacción entre aplicaciones.
9. Modelo técnico de implementación en Django REST
La implementación recomendada se basa en Django, Django REST Framework, PostgreSQL y autenticación JWT. La lógica de negocio debe residir en services, no en views. Los ViewSets coordinan entrada/salida HTTP, los serializers validan estructura de datos y los services ejecutan reglas de negocio.
9.1 Arquitectura por capas
Capa	Responsabilidad	Ejemplos Django
Presentación / API	Exponer recursos REST, autenticar, serializar respuestas	ViewSets, routers, JWT, permissions
Aplicación / servicios	Aplicar reglas de negocio y coordinar transacciones	PedidoService, CreditoService, PuntosService
Dominio / modelos	Representar entidades, relaciones y restricciones	models.py por app
Persistencia	Guardar datos y mantener integridad	PostgreSQL, migraciones, constraints
Integración	Comunicar eventos externos o internos	email backend, servicios REST, tasks si se justifica

9.2 Apps Django recomendadas
App	Responsabilidad principal	Prioridad
authentication	Login, JWT, refresh, permisos base	Crítica
users	Usuario, perfil cliente, roles internos	Crítica
products	Productos, categorías, precios	Crítica
inventory	Stock por producto y sucursal, reservas, movimientos	Crítica
cart	Carrito y líneas temporales	Alta
orders	Pedido, detalle, estados, voucher	Crítica
payments	Pagos electrónicos, transferencia, estado de pago	Crítica
credit	FerreCrédito, cupo, cuotas, deuda, validaciones	Crítica
loyalty	Cuenta de puntos y movimientos	Alta
maestros	Perfil Maestro/PYME, servicios publicados, asesorías	Crítica
surveys	Encuesta de satisfacción postventa	Media-Alta
notifications	Correos, avisos y contacto cliente-maestro	Alta
reports	Reportes de ventas, puntos, crédito y satisfacción	Media
integrations	Servicios internos o wrappers de integración	Media

9.3 Entidades principales
Entidad	Campos clave	Relaciones
Usuario	email, password, rol, is_active	1 a 1 con PerfilCliente / PerfilMaestroPyme
PerfilCliente	usuario, rut, nombre, teléfono, dirección	1 a N con Pedido y CuentaPuntos
PerfilMaestroPyme	usuario, rubro, oficio, empresa, aprobado, descuento_usado	1 a 1 con CuentaCredito; 1 a N ServiciosMaestro
Producto	sku, nombre, precio, categoría, activo	N a 1 Categoría; 1 a N Inventario
Inventario	producto, sucursal, stock_disponible, stock_reservado	N a 1 Producto
Pedido	cliente, estado, subtotal, descuento, puntos_usados, total_final, tipo_entrega	1 a N DetallePedido; 1 a 1 Pago/Voucher
DetallePedido	pedido, producto, cantidad, precio_unitario, tipo_linea	Puede representar producto o asesoría de maestro
Pago	pedido, medio_pago, monto, estado, referencia	1 a 1 Pedido
CuentaCredito	maestro_pyme, cupo_aprobado, saldo_usado, estado	1 a N CompraCredito
CompraCredito	cuenta, pedido, monto, numero_cuotas, estado	1 a N CuotaCredito
CuotaCredito	compra_credito, número, monto, vencimiento, estado	Control mensual
CuentaPuntos	cliente, saldo_actual	1 a N MovimientoPuntos
MovimientoPuntos	cuenta, tipo, puntos, pedido, saldo_resultante	Auditoría de puntos
ServicioMaestro	maestro_pyme, título, descripción, rubro, activo	Publicación visible en ecommerce
SolicitudServicioMaestro	pedido, servicio, cliente, maestro, cargo_confirmacion	Genera voucher y correo mixto
EncuestaSatisfaccion	pedido, cliente, puntaje, comentario	Postventa
VoucherCompra	pedido, contenido, datos_maestro, generado_en	Comprobante de compra

9.4 Estados del pedido y transiciones mínimas
Estado	Quién puede cambiarlo	Condición
pedido_creado	Cliente / sistema	Pedido generado desde carrito
stock_validado	Sistema / bodeguero	Stock suficiente o reservado
pedido_aprobado	Vendedor / sistema	Stock y reglas comerciales válidas
pedido_rechazado	Vendedor / sistema	Stock insuficiente, pago rechazado o crédito inválido
pago_pendiente	Sistema	Pago no confirmado o transferencia por validar
pago_confirmado	Pasarela / contador	Pago recibido o FerreCrédito autorizado
en_preparacion	Bodeguero	Pedido pagado/aprobado
listo_para_retiro	Bodeguero	Pedido preparado para retiro
en_despacho	Bodega / logística	Pedido preparado para despacho
entregado	Bodega / vendedor	Cliente recibió producto
cerrado	Sistema / contador	Entrega finalizada, puntos aplicados/acumulados, encuesta habilitada

9.5 APIs REST mínimas
Recurso	Métodos mínimos	Responsabilidad
/api/auth/	POST	Login, refresh token, logout
/api/productos/	GET, POST, PATCH	Catálogo y administración de productos
/api/inventario/	GET, PATCH	Consulta y ajuste de stock
/api/carrito/	GET, POST, DELETE	Construcción de compra
/api/pedidos/	GET, POST, PATCH	Creación, consulta y actualización de pedido
/api/pedidos/{id}/estado/	PATCH	Cambio controlado de estado
/api/pagos/	POST, GET	Confirmación y seguimiento de pago
/api/credito/validar-compra/	POST	Autorizar compra con FerreCrédito
/api/credito/cuentas/	GET, PATCH	Administrar cupos y estado de cuenta
/api/maestros-pyme/	GET, POST, PATCH	Registro y administración de perfiles
/api/servicios-maestro/	GET, POST, PATCH	Publicación y contratación de servicios
/api/puntos/	GET, POST	Consultar, aplicar y acumular puntos
/api/encuestas/	GET, POST	Responder y consultar encuestas
/api/notificaciones/	POST	Enviar correo mixto y avisos
/api/reportes/	GET	Ventas, crédito, puntos, satisfacción

10. Comparación As Is vs To Be
Criterio	As Is	To Be	Impacto esperado
Canal de venta	Principalmente presencial	Híbrido: tienda + web	Mayor cobertura y continuidad
Visibilidad del pedido	Baja	Alta y basada en estados	Mejor experiencia y control
Coordinación entre áreas	Manual / secuencial	Servicios y flujos visibles	Menos fricción operativa
Consulta de stock	Interna y con intervención humana	Disponible al proceso digital	Mejor decisión de compra
Medios de pago	Tradicionales	Débito, crédito, transferencia y FerreCrédito	Más opciones y crédito interno
Trazabilidad	Fragmentada	Centralizada por estados y eventos	Control y auditoría
Fidelización	No existe esquema digital	Puntos acumulables y descuentos por puntos	Mayor recompra
Servicios asociados	No existe derivación estructurada	Maestros/PYMES publican servicios y asesorías	Valor agregado
Cliente Maestro PYME	Sin tratamiento digital	Vista, descuento 30%, FerreCrédito, servicios	Segmentación comercial
Postventa	Sin encuesta estructurada	Encuesta posterior a entrega/cierre	Mejora continua basada en datos
Pago e inventario	Relación no automatizada	Pago confirmado gatilla ajuste de stock	Coherencia entre venta, pago y bodega
Crédito interno	No existe	Cupo, cuotas y deuda al día gestionada por admin	Inclusión financiera controlada

11. Matriz de cobertura de la pauta y requerimientos adicionales
Indicador / RF	Cobertura en informe corregido	Sección asociada	Estado
Modelo de negocio	Se describen negocio, problema, actores, procesos y clasificación	4 y 5	Cubierto
Procesos de integración	Se identifican procesos clave y sistemas involucrados	5.3, 8.1, 8.2	Cubierto
BPMN As Is / To Be	Se incluyen diagramas resumidos y espacios formales	6.6, 7.9	Cubierto
Webservices y ubicación	Servicios definidos por dueño del dato y consumidor	8.3, 8.4	Cubierto
Vista Maestro/PYME	Se define vista, registro y perfil especial	7.3, 7.5, 9.2	Cubierto
Descuento primera compra 30%	Regla RN-04 y endpoint de aplicación	7.6, 8.4	Cubierto
FerreCrédito	Cuenta corriente interna, cupo, deuda y cuotas	7.5, 7.6, 9.3	Cubierto
Segunda compra con crédito al día	Regla RN-06 y validación técnica	7.6, 8.4	Cubierto
Cupo aprobado por admin	Regla RN-07/RN-08 y endpoints protegidos	7.6, 8.4	Cubierto
Servicios de maestros	Publicación, contratación de asesoría y contacto	7.5, 8.4, 9.3	Cubierto
Cobro fijo $5.000	Línea de pedido tipo asesoría_confirmacion	7.6, 9.3	Cubierto
Correo mixto y voucher	WS_Notificaciones y WS_Voucher	8.3, 8.4	Cubierto
Pago final externo	Regla RN-12, no registrar ingreso final de servicio	7.6, 12	Cubierto
Encuesta satisfacción	Módulo postventa y API de encuestas	7.8, 9.5	Cubierto
Puntos acumulables	CuentaPuntos y MovimientoPuntos	7.6, 9.3	Cubierto

12. Riesgos, controles e inconsistencias corregidas
Riesgo detectado	Por qué afecta	Corrección aplicada en este informe
Maestro PYME tratado solo como recomendación	No cubre vista, registro ni crédito interno	Se define subdominio Maestro PYME con perfil, vista, servicios y FerreCrédito.
Cuenta corriente demasiado genérica	El profesor pide FerreCrédito con reglas específicas	Se agregan cupo, cuotas, deuda al día y gestión por administrador.
Descuento no cuantificado	El RF exige 30% en primera compra	Se agrega RN-04 y endpoint de aplicación.
Servicio maestro confundido con venta de Ferremas	El pago final no pasa por sistemas Ferremas	Se distingue cargo de confirmación de $5.000 y pago final externo.
Falta de correo/voucher	RF exige poner en contacto a cliente y maestro	Se agregan WS_Notificaciones y WS_Voucher.
Puntos sin control de remanente	Podría descontarse saldo incorrectamente	Se agrega CuentaPuntos y MovimientoPuntos transaccional.
Lógica en views	Reduce mantenibilidad	Se recomienda services para reglas de negocio.

13. Conclusiones
El levantamiento del negocio de FERREMAS permite concluir que la empresa posee una estructura operativa clara, pero aún dependiente de atención presencial y coordinación manual. El proceso principal de venta está soportado por inventario, registro financiero y supervisión administrativa, lo que evidencia una organización funcional pero limitada por falta de integración y ausencia de canal digital.
La propuesta To Be corrige esta debilidad mediante ecommerce, trazabilidad por estados, integración REST y módulos especializados. La actualización del caso exige ampliar el alcance más allá de un ecommerce básico: se requiere integrar Maestro PYME, FerreCrédito, puntos, servicios asociados, voucher, correo mixto y encuesta virtual.
La solución técnica propuesta en Django REST Framework queda alineada con arquitectura por capas: presentación/API, services de negocio, modelos de dominio, persistencia PostgreSQL e integración mediante webservices. La separación por apps evita mezclar responsabilidades y permite defender académicamente la relación entre documentación, procesos, APIs y backend.
Finalmente, el informe corregido deja explícitas las reglas de negocio críticas que faltaban: 30% de descuento en primera compra Maestro/PYME, uso exclusivo de FerreCrédito, validación de deuda al día, control de cupo por administrador, cuotas mensuales, confirmación de asesoría de $5.000, contacto cliente-maestro por voucher/correo y exclusión del pago final del servicio profesional del sistema financiero de FERREMAS.
14. Referencias
1. Duoc UC. (2022). Evaluación Parcial 1: Análisis y Planificación - Caso FERREMAS [Material de cátedra]. Asignatura Integración de Plataformas, ASY5131.
2. Duoc UC. (2022). Conociendo los procesos de negocio [Presentación de clase]. Asignatura Integración de Plataformas, ASY5131.
3. Duoc UC. (2022). Identificando las capas de negocio [Presentación de clase]. Asignatura Integración de Plataformas, ASY5131.
4. Duoc UC. (2022). Construyendo diagrama BPMN [Presentación de clase]. Asignatura Integración de Plataformas, ASY5131.
5. Duoc UC. (2022). Webservices para la integración [Presentación de clase]. Asignatura Integración de Plataformas, ASY5131.
6. Caso FERREMAS - Requerimientos adicionales Maestro PYME, FerreCrédito, encuesta virtual y puntos acumulables.
7. Documentación oficial de Django y Django REST Framework, utilizada como referencia técnica para arquitectura REST, ViewSets, Serializers, Permissions y Services.
