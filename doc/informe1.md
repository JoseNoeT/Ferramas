FERREMAS | Evaluación Parcial 1 
Evaluación Parcial 1 
Análisis y Planificación de FERREMAS 
Modelo As Is, propuesta To Be e integración de webservices 
Asignatura 
Sigla 
Integración de Plataformas 
Institución 
ASY5131 
Carrera 
Duoc UC 
Profesor 
Ingeniería en Informática 
Estudiante 
Juan Alberto Ghana 
Fecha 
José Miguel Noe Torres 
Abril 2026 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Integración de Plataformas – ASY5131 
Tabla de contenido 
1. Introducción ......................................................................................................................................... 3 
2. Objetivos del informe ........................................................................................................................... 4 
2.1 Objetivo general ............................................................................................................................. 4 
2.2 Objetivos específicos ..................................................................................................................... 4 
3. Metodología de análisis ........................................................................................................................ 4 
4. Contexto del negocio y problema detectado ........................................................................................ 5 
5. Modelo de negocio actual de FERREMAS ......................................................................................... 5 
5.1 Actores y roles ................................................................................................................................ 6 
5.2 Procesos identificados y clasificación ............................................................................................ 6 
5.3 Procesos clave involucrados en la integración ............................................................................... 7 
5.4 Relación entre procesos y mapa general ........................................................................................ 8 
6. Análisis del estado actual (As Is) ......................................................................................................... 9 
6.1 Descripción general del proceso actual .......................................................................................... 9 
6.2 Secuencia operativa del flujo actual ............................................................................................... 9 
6.3 Entradas, salidas y recursos .......................................................................................................... 10 
6.4 Sistemas y capas del As Is ........................................................................................................... 11 
6.5 Debilidades del estado actual ....................................................................................................... 12 
6.6 Espacios para diagramas As Is ..................................................................................................... 13 
7. Propuesta de estado futuro (To Be) .................................................................................................... 16 
7.1 Objetivo de mejora ....................................................................................................................... 16 
7.2 Rediseño del proceso .................................................................................................................... 17 
7.3 Actores del To Be ......................................................................................................................... 18 
7.4 Experiencia del cliente ................................................................................................................. 19 
7.5 Capas afectadas y relación con sistemas existentes ..................................................................... 19 
7.6 Control y trazabilidad ................................................................................................................... 20 
7.7 Espacios para diagramas To Be ................................................................................................... 21 
8. Integración de plataformas y webservices ......................................................................................... 23 
8.1 Necesidad real de integración ...................................................................................................... 23 
8.2 Objetos de negocio y datos que viajan ......................................................................................... 24 
8.3 Propuesta y ubicación de webservices ......................................................................................... 25 
8.4 Relación con REST, seguridad e interacción entre servicios ....................................................... 27 
8.5 Espacios para diagramas de arquitectura y servicios ................................................................... 28 
9. Comparación As Is vs To Be ............................................................................................................. 29 
10. Matriz de cobertura de la pauta ........................................................................................................ 31 
FERREMAS | Evaluación Parcial 1 
11. Conclusiones .................................................................................................................................... 31 
12. Referencias ....................................................................................................................................... 32 
1. Introducción 
El presente informe desarrolla la etapa de análisis y planificación del caso 
FERREMAS en el contexto de la asignatura Integración de Plataformas. Su propósito es 
estudiar el negocio, describir el estado actual de operación, proyectar un estado futuro 
orientado al comercio electrónico e identificar los puntos de integración que justifican el uso 
de webservices dentro de una arquitectura por capas. 
El documento no se limita a una descripción aislada del As Is. Por el contrario, 
organiza el levantamiento del negocio de modo que el diagnóstico del proceso actual sirva 
como base para el diseño del To Be y para la posterior definición de la integración 
tecnológica. Esto permite mantener una línea lógica entre negocio, procesos, BPMN, capas 
afectadas y servicios de integración. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
La evaluación requiere identificar el modelo de negocio, reconocer los procesos 
involucrados, representar el flujo actual y las mejoras propuestas mediante BPMN, y definir 
webservices de acuerdo con la arquitectura de software y hardware. Por ello, el informe se 
estructura como una pieza única que conecta diagnóstico, rediseño e integración en un solo 
análisis técnico. 
2. Objetivos del informe 
2.1 Objetivo general 
Analizar y planificar la situación actual y futura de FERREMAS mediante la 
identificación del modelo de negocio, el levantamiento del proceso operativo principal en su 
estado As Is, la propuesta de un modelo To Be orientado al comercio electrónico y la 
definición de integraciones mediante webservices, con el fin de fundamentar una solución 
coherente con las necesidades del negocio. 
2.2 Objetivos específicos 
• Identificar el modelo de negocio, el problema detectado, los actores y los 
procesos involucrados en la operación. 
• Clasificar los procesos de FERREMAS en operativos, de apoyo, de gestión y 
estratégicos, justificando su clasificación. 
• Describir el estado actual del proceso principal, incluyendo flujo, entradas, 
salidas, recursos, sistemas y capas afectadas. 
• Proponer un modelo To Be alineado con la necesidad de comercio electrónico 
planteada por el caso. 
• Detectar los puntos de integración necesarios y definir webservices ubicados 
de forma coherente con la arquitectura de software. 
• Dejar una estructura documental lista para incorporar los diagramas BPMN, el 
mapa de procesos y los esquemas de arquitectura e integración. 
3. Metodología de análisis 
Para desarrollar el informe se utilizó una metodología por etapas. Primero, se revisó el 
caso FERREMAS para comprender el contexto del negocio, el problema central y los roles 
definidos en la organización. Luego, se identificaron los procesos presentes en la operación y 
se clasificaron según su relación con el valor entregado al cliente. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
En una segunda etapa, se levantó el estado actual del proceso principal, 
descomponiéndolo en actores, actividades, entradas, salidas, recursos, sistemas y capas 
afectadas. Este paso permitió separar con claridad la realidad operativa vigente de la solución 
futura, evitando mezclar el proceso actual con la propuesta de comercio electrónico. 
Finalmente, a partir de las debilidades del As Is, se proyectó un modelo To Be y se 
determinaron los puntos de integración que requieren intercambio de datos entre sistemas. 
Con ello, fue posible proponer webservices, justificar su ubicación en la arquitectura y 
preparar el informe para su representación gráfica en BPMN y diagramas de servicios. 
4. Contexto del negocio y problema detectado 
FERREMAS es una distribuidora de productos de ferretería y construcción con 
presencia en la Región Metropolitana y en regiones, con proyección de expansión nacional. 
Comercializa herramientas manuales y eléctricas, pinturas, materiales eléctricos, accesorios y 
artículos de seguridad, trabajando con marcas reconocidas del sector. 
La empresa opera mediante sucursales físicas con una estructura organizativa definida. 
Cada tienda cuenta con administrador, vendedor o encargado, bodeguero y contador, actores 
que participan en la venta, la preparación de productos, el control financiero y la supervisión 
del desempeño comercial. 
El problema central detectado en el caso es la ausencia de una plataforma de venta en 
línea. Durante la pandemia, la empresa sufrió una disminución en sus ventas físicas debido a 
la dependencia del canal presencial, lo que evidenció la necesidad de evolucionar hacia un 
modelo híbrido que combine atención en sucursal y comercio electrónico. 
5. Modelo de negocio actual de FERREMAS 
El modelo de negocio actual de FERREMAS se sostiene principalmente sobre la venta 
presencial de productos en sucursal. El valor entregado al cliente proviene de la 
disponibilidad de productos, la variedad de marcas, la asesoría comercial y la capacidad de 
concretar una compra con entrega inmediata en tienda. 
Desde la perspectiva del ramo, el proceso principal es aquel que transforma entradas 
en salidas con valor para el cliente. En este caso, dicho proceso corresponde a la venta 
presencial de productos. A su alrededor operan procesos de apoyo, gestión y orientación 
estratégica que permiten que la venta se ejecute, se registre y se controle correctamente. 
Integración de Plataformas – ASY5131 
5.1 Actores y roles 
FERREMAS | Evaluación Parcial 1 
Actor 
Rol 
principal 
Responsabilidades en el estado actual 
Adminis
trador 
Gestión y 
supervisión 
Genera informes mensuales, revisa 
desempeño y define promociones o estrategias de 
venta. 
Vendedo
r / Encargado 
Atención 
comercial 
Bodegue
ro 
Asesora al cliente, recibe el pedido, coordina 
con bodega y gestiona pago y facturación. 
Apoyo 
operativo e 
inventario 
Contado
r 
Consulta stock, organiza bodega, prepara 
productos y los entrega para la venta. 
Registra transacciones, controla pagos, 
apoya validaciones financieras y elabora balances o 
reportes financieros. 
Control 
financiero 
Cliente 
Demandan
te del servicio 
Solicita productos, recibe orientación, 
compra y recibe el bien adquirido. 
5.2 Procesos identificados y clasificación 
A partir del caso se identifican procesos operativos, de apoyo, de gestión y un proceso 
estratégico visible. La clasificación se fundamenta en la relación de cada proceso con el valor 
entregado al cliente, con el soporte interno de la venta y con el monitoreo del negocio. La 
clasificación se fundamenta en la relación de cada proceso con el valor entregado al cliente, 
con el soporte interno de la venta y con el monitoreo general del negocio 
Proceso 
Tipo 
Objetivo 
Justificación 
Venta 
presencial de 
productos 
Operativo 
Concretar 
la venta 
Genera 
directamente el 
producto/servicio que 
recibe el cliente. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Integración de Plataformas – ASY5131 
Atención y 
asesoría comercial Operativo Orientar la 
compra 
Forma parte del 
proceso que termina en la 
venta y satisfacción del 
cliente. 
Gestión de 
inventario y 
preparación 
Apoyo Asegurar 
disponibilidad 
Permite que la venta 
se concrete, pero por sí sola 
no entrega valor final al 
cliente. 
Facturación 
y registro 
financiero 
Apoyo / 
gestión operativa 
Formalizar 
y controlar la 
transacción 
Hace posible la 
venta ordenada y deja 
trazabilidad financiera. 
Informes de 
venta y desempeño 
Gestión Monitorear 
el proceso 
Mide resultados y 
apoya el control del 
negocio. 
Estrategias 
de venta y 
promociones 
Estratégico 
Orientar la 
dirección 
comercial 
No vende 
directamente, pero define 
mejoras y foco comercial. 
 
5.3 Procesos clave involucrados en la integración 
Para cubrir la pauta con un nivel alto, se distinguen cuatro procesos clave involucrados 
en la futura integración. Estos procesos son los que más directamente deberán intercambiar 
información en el To Be y muestran que FERREMAS no solo necesita ecommerce, sino 
también trazabilidad, fidelización y servicios complementarios de negocio. 
Proces
o clave Tipo Objetivo 
Sistema
s / datos 
involucrados 
Necesida
d de integración 
Gestió
n de venta y 
pedido 
Operativ
o 
Registrar 
y canalizar la 
compra 
Catálog
o, cliente, 
Alta 
FERREMAS | Evaluación Parcial 1 
Gestió
n de inventario 
y preparación 
Apoyo 
operativo 
pedido, total de 
compra 
Stock, 
ubicación, 
estado de 
preparación 
Validar 
stock y preparar 
productos 
Gestió
n de pago y 
facturación 
Apoyo 
operativo 
Confirma
r pago y 
formalizar la 
transacción 
Alta 
Monto, 
medio de pago, 
comprobante 
Gestió
n de entrega y 
trazabilidad 
Operativ
o / control 
Despacha
r, retirar y cerrar 
el pedido 
Alta 
Estado 
del pedido, 
entrega, 
confirmación 
5.4 Relación entre procesos y mapa general 
Alta 
Los procesos se relacionan de forma encadenada. El cliente solicita un producto, 
el vendedor orienta y registra el pedido, el bodeguero verifica la disponibilidad y prepara los 
productos, el contador registra la transacción y controla el pago, y el administrador supervisa 
resultados, genera informes de desempeño y apoya la toma de decisiones comerciales. De esta 
manera, el proceso operativo principal de venta presencial se sostiene mediante procesos de 
apoyo asociados a bodega e inventario, además del registro financiero, mientras la 
administración participa desde la gestión y supervisión general del negocio. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
6. Análisis del estado actual (As Is) 
6.1 Descripción general del proceso actual 
En el estado actual, el proceso principal de FERREMAS se desarrolla mediante 
atención presencial. El flujo comienza cuando el cliente llega a la sucursal y solicita asesoría 
o un producto. A partir de ese momento, el vendedor se convierte en el principal punto de 
contacto comercial y coordina la continuidad del proceso con bodega y contabilidad. 
El As Is revela una operación funcional, pero altamente dependiente de la 
presencialidad y de la coordinación secuencial entre áreas. Aunque la empresa mantiene orden 
interno gracias a la separación de roles, la venta no funciona como un proceso aislado, ya que 
depende de la validación de stock, del cobro o facturación y del registro financiero posterior 
6.2 Secuencia operativa del flujo actual 
Paso 
Actor 
responsable 
Actividad actual 
1 
Cliente 
Visita la tienda o solicita atención 
comercial. 
Integración de Plataformas – ASY5131 
2 
FERREMAS | Evaluación Parcial 1 
Asesora al cliente e identifica la 
necesidad de compra. 
3 
Vendedor / 
Encargado 
Vendedor / 
Encargado 
Recibe y procesa el pedido. 
4 
Bodeguero 
Verifica disponibilidad y prepara los 
productos solicitados. 
5 
Vendedor / 
Encargado 
Gestiona el pago y la facturación de 
la venta. 
6 
Contador 
Registra la transacción y controla los 
pagos. 
7 
Administrador 
Supervisa resultados mediante 
informes y seguimiento del desempeño. 
Dentro del flujo actual existen validaciones de stock, pago, facturación y registro. 
También aparecen decisiones relacionadas con la existencia o no de productos disponibles y 
con la correcta concreción del pago. En el estado actual, el proceso depende de la 
coordinación secuencial entre atención comercial, bodega, contabilidad y supervisión 
administrativa. 
6.3 Entradas, salidas y recursos 
Elemento 
Descripción 
Entrada que 
activa el proceso 
Solicitud de compra del cliente. 
Información 
requerida 
Producto solicitado, precio, disponibilidad de stock, medio 
de pago y datos para facturación. 
Recursos 
utilizados 
Personal de tienda, bodega, caja o punto de venta, sistemas 
internos de apoyo y registros administrativos/contables. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Salida del 
proceso 
Venta concretada y registrada. 
Resultado 
para el cliente 
Producto entregado y comprobante de 
compra. 
Registros 
generados 
Registro de venta, boleta o factura, registro contable y datos 
para reportes de control. 
6.4 Sistemas y capas del As Is 
Aunque el caso no nombra software específico, para representar correctamente el As 
Is se infieren sistemas mínimos coherentes con las funciones descritas. Esta inferencia permite 
que el flujo actual quede completo y defendible, mostrando las actividades de ventas, bodega, 
facturación, contabilidad y supervisión administrativa. 
Sistema / 
componente 
Respons
able principal 
Uso en el As Is 
Sistema de 
ventas en sucursal 
Vendedo
r 
Registrar pedido, consultar precio, 
calcular venta y gestionar cobro. 
Módulo de 
inventario / bodega 
Bodegue
ro 
Consultar stock, organizar inventario y 
preparar productos para la venta. 
Sistema de 
facturación / caja 
Vendedo
r / caja 
Emitir comprobante y dejar constancia 
del pago. 
Sistema 
contable / financiero 
Contado
r 
Registrar transacciones, controlar pagos y 
elaborar balances. 
Módulo 
administrativo de 
reportes 
Adminis
trador 
Generar informes y revisar el desempeño 
general de la tienda. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Comunicació
n operativa manual 
Áreas 
internas 
Coordinar traspasos de información entre 
vendedor, bodega y contabilidad. 
Desde la arquitectura por capas, la presentación corresponde a la interacción en 
mostrador, caja y terminales de atención; la capa de negocio concentra la validación de stock, 
el procesamiento del pedido, el cálculo del total y el cierre de la venta; y la capa de datos 
almacena catálogo, inventario, ventas, pagos, comprobantes, reportes y registros contables. 
Capa 
Qué ocurre en FERREMAS As Is 
Impacto del 
problema actual 
Present
ación 
Atención presencial, captura del pedido y 
uso de terminales internas. 
Muy alto: no 
existe canal digital 
para el cliente. 
Negoci
o 
Validación de stock, procesamiento del 
pedido, cálculo del total, control de condiciones 
de negocio, cierre de la venta 
Alto: la lógica 
sigue centrada en la 
presencialidad. 
Datos 
Catálogo, inventario, ventas, pagos, 
boletas/facturas, registros contables y reportes. 
6.5 Debilidades del estado actual 
Medio-Alto: 
no existe flujo digital 
integrado de pedidos 
y estados. 
El estado actual de FERREMAS presenta tareas manuales repetidas en la atención al 
cliente, la consulta de stock, la coordinación con bodega, la facturación y el registro 
financiero. Esta fragmentación genera demoras, posibles duplicidades de información y una 
baja visibilidad integral del proceso entre las distintas áreas involucradas. 
Además, la empresa depende principalmente de la atención presencial para concretar 
la venta, lo que limita la continuidad operativa y reduce la flexibilidad comercial frente a 
escenarios que exigen canales alternativos de atención. A ello se suma la ausencia de un flujo 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
digital integrado que permita consultar productos, registrar pedidos, dar seguimiento al estado 
de la compra y coordinar de manera más eficiente las actividades entre ventas, bodega y 
contabilidad. 
En el estado actual tampoco existe una gestión digital integrada de fidelización por 
puntos, encuestas postventa, recomendación de servicios asociados ni actualización 
automática del inventario una vez confirmada la venta., fidelización por puntos, encuestas 
postventa, recomendación de servicios asociados ni actualización automática del inventario 
una vez confirmada la venta. Estas limitaciones afectan tanto la experiencia del cliente como 
la capacidad de control y trazabilidad de la empresa. 
Para el cliente, las principales fricciones son la necesidad de acudir físicamente a la 
sucursal, la imposibilidad de revisar catálogo o comprar en línea y la falta de seguimiento del 
pedido. Para la organización, la principal debilidad es mantener un flujo tradicional, 
secuencial y poco integrado, lo que justifica el rediseño del modelo To Be y la incorporación 
posterior de servicios e integración tecnológica. 
6.6 Espacios para diagramas As Is 
Figura 2. BPMN As Is del proceso operativo principal de venta presencial 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Fuente: elaboración propia en Bizagi. 
Figura 3. BPMN As Is del proceso operativo de gestión de inventario y 
preparación 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Fuente: elaboración propia en Bizagi / diagrama del estudiante. 
Figura 4. BPMN As Is del proceso de facturación, registro y control financiero 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Fuente: elaboración propia en Bizagi / diagrama del estudiante. 
7. Propuesta de estado futuro (To Be) 
7.1 Objetivo de mejora 
El To Be busca resolver la dependencia de la venta presencial, la falta de canal digital, 
la baja visibilidad del estado del pedido y la coordinación manual entre áreas. El nuevo 
proceso debe permitir a FERREMAS operar de forma híbrida, incorporando ecommerce, 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
actualización automática del inventario, fidelización por puntos, beneficios para Maestro 
PYME y postventa con encuesta de satisfacción. 
Desde la perspectiva del cliente, la mejora principal es poder buscar productos, 
comprar en línea, seleccionar retiro o despacho, usar distintos medios de pago y consultar el 
estado del pedido. Para la organización, el objetivo es aumentar continuidad operativa, 
cobertura comercial, trazabilidad y valor agregado mediante descuentos por puntos, servicios 
asociados y segmentación de clientes especiales. 
7.2 Rediseño del proceso 
En el To Be, el proceso debería iniciar en el sitio web, cuando el cliente navega por el 
catálogo, inicia sesión o se registra y genera un pedido. Se mantienen actividades clave como 
la validación de stock, la preparación en bodega, el control de pagos, el registro contable y la 
supervisión administrativa, pero se reducen actividades manuales innecesarias. El rediseño 
incorpora funcionalidades nuevas solicitadas o reforzadas por el profesor: gestión de puntos 
acumulables, descuentos por puntos, encuesta de satisfacción postventa, módulo Maestro 
PYME, posibilidad de cuenta corriente o compra a crédito para ese segmento y 
recomendación de instalación cuando el cliente compra productos como cerámica. 
Entre las actividades que deben automatizarse se encuentran la consulta de catálogo, el 
registro del pedido, la validación de stock, la actualización de estados, la notificación del 
avance y parte de la confirmación del pago. Además, cuando el pago se confirma, un 
webservices debe actualizar el inventario automáticamente; y cuando el producto lo amerita, 
la plataforma debe poder sugerir o conectar al cliente con un Maestro PYME que ofrezca el 
servicio asociado. Luego del cierre o de la entrega, el proceso debe habilitar una encuesta de 
satisfacción para retroalimentación y mejora continua. También deben modelarse decisiones 
adicionales: cliente normal o Maestro PYME, compra estándar o compra con cuenta 
corriente/crédito, uso de puntos para descuento y necesidad o no de recomendación de 
instalación/servicio. 
• Decisión 1: cliente registrado o no registrado. 
• Decisión 2: existe stock o no existe stock. 
• Decisión 3: retiro en tienda o despacho a domicilio. 
• Decisión 4: pago aprobado, pendiente o en validación manual. 
• Decisión 5: pedido aprobado o rechazado por el área correspondiente. 
Integración de Plataformas – ASY5131 
7.3 Actores del To Be 
FERREMAS | Evaluación Parcial 1 
Los actores base se mantienen, pero sus responsabilidades cambian por la 
incorporación del sistema web. Además, aparecen nuevos actores y perfiles relevantes: la 
plataforma ecommerce, un sistema externo de pago, el cliente Maestro PYME como 
segmento especial y el Maestro prestador de servicios que puede publicar u ofrecer su 
especialidad en la plataforma. 
Actor 
Responsabilidad en el To Be 
Cliente web 
Navega por catálogo, registra pedido, elige 
entrega y consulta estado. 
Vendedor 
Aprueba o rechaza pedidos, organiza despacho 
y da seguimiento operativo. 
Bodeguero 
Recibe órdenes digitales, prepara productos y 
actualiza estado. 
Contador 
Confirma transferencias, controla pagos y 
registra entrega/cierre financiero. 
Administrador 
Gestiona usuarios, monitorea desempeño y 
controla la operación digital. 
Sistema web / ecommerce 
Canaliza pedidos, muestra catálogo, registra 
estados y comunica áreas. 
Pasarela o sistema externo 
de pago 
Autoriza o confirma pagos electrónicos. 
Maestro PYME 
Actúa como cliente con beneficios especiales y 
también como posible prestador de servicios en la 
plataforma; puede comprar materiales, acceder a 
cuenta corriente o compra a crédito, publicar u ofrecer 
su servicio y ser recomendado cuando la compra del 
cliente requiere instalación o apoyo técnico. 
Integración de Plataformas – ASY5131 
7.4 Experiencia del cliente 
FERREMAS | Evaluación Parcial 1 
En el estado futuro, el cliente podrá ejecutar acciones que hoy no puede realizar: 
comprar en línea, revisar un catálogo digital, utilizar un carrito de compras, seleccionar retiro 
o despacho, pagar electrónicamente, consultar el estado del pedido y acceder a beneficios de 
fidelización. La plataforma también podrá mostrar puntos acumulados, descuentos aplicables, 
recomendaciones de servicios y beneficios diferenciados para el segmento Maestro PYME. 
Estas mejoras eliminan fricciones del As Is, como la necesidad de desplazarse siempre 
a la sucursal, la falta de visibilidad del avance de la compra y la dependencia del contacto 
presencial para tareas simples. Además, agregan valor de negocio: puntos canjeables, 
encuesta de satisfacción postventa, acceso a cuenta corriente o crédito para Maestro PYME y 
recomendación de instalación cuando el producto adquirido lo requiera, por ejemplo, en 
compras de cerámica. 
7.5 Capas afectadas y relación con sistemas existentes 
La capa de presentación cambia con la incorporación del sitio web, el inicio de sesión, 
el catálogo virtual, el carrito, el checkout y paneles internos por rol. También se agregan 
vistas para puntos, descuentos, beneficios del cliente Maestro PYME, publicación o 
recomendación de servicios y encuesta de satisfacción. 
Aspecto 
As Is 
To Be 
Canal principal 
Atención presencial 
Canal híbrido: tienda + 
ecommerce 
Consulta de 
productos 
Presencial o interna 
Catálogo en línea y 
consulta interna 
Gestión del pedido 
Secuencial y manual 
Registrada digitalmente y 
visible por estado 
Visibilidad del flujo 
Baja 
Alta para cliente y áreas 
internas 
Coordinación entre 
áreas 
Principalmente manual 
Apoyada por servicios y 
estados digitales 
Integración de Plataformas – ASY5131 
Fidelización 
FERREMAS | Evaluación Parcial 1 
Puntos acumulables y 
descuentos por puntos 
Servicios 
complementarios 
No existe esquema 
digital de puntos 
No hay derivación 
digital 
Recomendación de 
Maestro PYME según producto 
comprado 
Segmento Maestro 
PYME 
Cuenta corriente, crédito y 
visibilidad de servicios 
Postventa 
No tiene tratamiento 
digital diferenciado 
Sin encuesta 
estructurada 
Actualización no 
completamente automática 
Encuesta de satisfacción 
postventa 
Inventario tras pago 
Actualización automática 
vía webservices 
El sistema nuevo que aparece es la plataforma web de comercio electrónico. No 
obstante, la solución no exige rehacer toda la infraestructura existente. La estrategia correcta 
es mantener la base operativa actual y conectarla mediante servicios con módulos nuevos de 
fidelización, Maestro PYME, recomendación de servicio y actualización automática de 
inventario una vez confirmado el pago. 
7.6 Control y trazabilidad 
El To Be debe hacer visibles los estados del proceso para todos los actores relevantes. 
Se propone como mínimo la siguiente secuencia de estados: pedido creado, stock validado, 
pedido aprobado, pedido rechazado, en preparación, pago confirmado, en despacho, listo para 
retiro, entregado y cerrado. A esta trazabilidad se suman eventos de negocio como uso y 
acumulación de puntos, aplicación de descuentos, solicitud de recomendación de Maestro 
PYME, oferta de servicio asociado y respuesta de la encuesta de satisfacción. 
Cada actor conocerá la etapa del proceso mediante paneles e indicadores visibles en el 
sistema. A su vez, deberán quedar registrados eventos como la creación del pedido, la 
aprobación o rechazo, la confirmación de stock, la preparación, la confirmación del pago, la 
actualización automática del inventario, la entrega o retiro, el cierre del proceso y la 
retroalimentación postventa. 
Integración de Plataformas – ASY5131 
7.7 Espacios para diagramas To Be 
FERREMAS | Evaluación Parcial 1 
Figura 5. Mapa general de procesos de FERREMAS (To Be  ) 
Fuente:  diagrama del estudiante. 
Figura 6. BPMN To Be del proceso operativo principal de venta integrada con 
ecommerce 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Fuente: elaboración propia en Bizagi / diagrama del estudiante. 
Figura 7. BPMN To Be del proceso de preparación, despacho o retiro y cierre del 
pedido 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Fuente: elaboración propia en Bizagi / diagrama del estudiante. 
8. Integración de plataformas y webservices 
8.1 Necesidad real de integración 
La consulta de stock en tiempo real, la creación del pedido, la actualización de 
estados, la confirmación de pagos y la trazabilidad del flujo no pueden funcionar 
correctamente sin integración. En el To Be reforzado por el profesor, también dependen de 
integración la acumulación y consumo de puntos, la recomendación de Maestro PYME, la 
publicación de servicios asociados y la actualización automática del inventario cuando el pago 
se confirma. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Por tanto, la necesidad real de integración se manifiesta cuando un sistema requiere 
datos que pertenecen a otro. En este caso, los sistemas que deben intercambiar información 
son, como mínimo, el ecommerce, inventario/bodega, pedidos, facturación, contabilidad, 
fidelización/puntos, módulo Maestro PYME y el sistema externo de pago. 
8.2 Objetos de negocio y datos que viajan 
El objeto de negocio principal que articula la integración es el pedido, ya que conecta 
cliente, productos, stock, pago, entrega y estado. Junto al pedido, también deben exponerse 
productos, stock, pagos, clientes, estados y nuevos objetos funcionales: puntos del cliente, 
tipo de cliente, cupo o condición comercial Maestro PYME, solicitud de recomendación, 
servicio ofrecido por el maestro y encuesta de satisfacción. 
Objeto / dato 
Dato que viaja 
Sistema dueño 
original 
Producto 
id Producto, 
nombre, precio, 
categoría 
Sistema de 
catálogo / 
ventas 
Sistema que 
consulta 
Sistema que 
actualiza 
Catálogo / 
ventas 
Ecommerce y 
paneles 
internos 
Stock 
id Producto, stock 
disponible, sucursal 
Inventario / 
bodega 
Inventario / 
bodega 
Ecommerce y 
vendedor 
Pedido 
id Pedido, detalle, 
total, cliente, estado 
Ecommerce / 
pedidos 
Ecommerce / 
pedidos 
Paneles 
internos 
Pago 
monto, medio, 
confirmación, 
referencia 
Pasarela + 
contabilidad 
Pasarela / 
contabilidad 
Ecommerce y 
contador 
Entrega / 
estado 
Puntos del 
cliente 
estado Pedido, 
fecha, tipoEntrega 
Bodega / 
módulo de 
estados 
Cliente y áreas 
internas 
Bodega / 
logística 
saldoPuntos, 
puntosGanados, 
puntosUsados 
Módulo de 
fidelización 
Ecommerce y 
panel 
comercial 
Integración de Plataformas – ASY5131 
Fidelización 
FERREMAS | Evaluación Parcial 1 
Tipo de cliente 
/ cupo 
comercial 
tipoCliente, cupo, 
condición de crédito 
Administración 
/ comercial 
Ecommerce y 
vendedor 
Administración 
/ comercial 
Servicio 
Maestro 
PYME / 
recomendación 
idMaestro, rubro, 
disponibilidad, 
recomendación 
Módulo 
Maestro 
PYME 
Módulo 
Maestro 
PYME 
Encuesta de 
satisfacción 
idEncuesta, puntaje, 
comentario, 
pedidoAsociado 
Ecommerce y 
cliente 
Módulo 
postventa 
Módulo 
postventa 
8.3 Propuesta y ubicación de webservices 
Administración 
/ calidad 
La ubicación del webservices debe decidirse según el sistema dueño del dato o de la 
lógica principal. De este modo se evita duplicar lógica, se mantiene la coherencia 
arquitectónica y se facilita la evolución del sistema. Además de los servicios base de 
productos, stock, pedidos, pagos, estados y entrega, el rediseño requiere servicios para 
fidelización, Maestro PYME, recomendación de servicios y encuesta postventa. También 
debe reforzarse que la confirmación de pago puede disparar la actualización automática del 
inventario mediante un servicio asociado. 
Webservices propuestos 
Qué expone 
Aplicación 
que expone 
Aplicación 
que consume 
WS_Productos 
Consulta de 
catálogo y 
detalle de 
productos 
Capa 
principa
l 
Catálogo / 
ventas 
WS_Stock 
Disponibilida
d por 
producto y 
sucursal; 
recibe 
actualización 
posterior al 
pago 
Ecommerce 
Negocio 
Inventario / 
bodega 
Ecommerce y 
vendedor 
Negocio 
+ datos 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Integración de Plataformas – ASY5131 
WS_Pedidos 
Registro y 
actualización 
de pedidos 
Ecommerce / 
pedidos 
Paneles 
internos Negocio 
WS_Pagos 
Confirmación 
y estado del 
pago; puede 
activar 
actualización 
automática de 
inventario 
Contabilidad / 
pasarela 
Ecommerce y 
contador Negocio 
    WS_EstadosPedido 
Seguimiento y 
cambios de 
estado 
Módulo de 
estados 
Cliente, 
vendedor y 
bodeguero 
Negocio 
WS_Entrega 
Confirmación 
de despacho, 
retiro y cierre 
Bodega / 
logística 
Ecommerce y 
contador Negocio 
WS_Puntos 
Consulta, 
acumulación 
y uso de 
puntos del 
cliente 
Módulo de 
fidelización 
Ecommerce y 
panel 
comercial 
Negocio 
    WS_EncuestaSatisfaccion 
Registro y 
consulta de 
evaluación 
postventa 
Módulo 
postventa / 
calidad 
Ecommerce y 
administració
n 
Negocio 
    
WS_MaestroPYME 
Consulta de 
perfiles, 
beneficios y 
servicios del 
Maestro 
PYME 
Módulo 
Maestro 
PYME 
Ecommerce y 
administració
n 
Negocio 
WS_RecomendacionServici
o 
Sugerencia de 
maestro o 
servicio 
asociado 
según 
producto 
comprado 
Motor de 
recomendació
n / Maestro 
PYME 
Ecommerce Negocio 
 
Estos servicios dialogan con la arquitectura actual sin romperla, ya que se insertan 
como una capa de servicios sobre o entre los sistemas existentes. La presentación consume el 
resultado; la lógica principal reside en negocio; y los sistemas dueños del dato mantienen la 
FERREMAS | Evaluación Parcial 1 
autoridad sobre stock, pagos, puntos, beneficios, perfiles Maestro PYME y registros 
postventa. 
8.4 Relación con REST, seguridad e interacción entre servicios 
Los servicios propuestos se entienden mejor como recursos de negocio que como 
procedimientos aislados. Por ello, el enfoque REST resulta adecuado: un cliente —por 
ejemplo, el ecommerce o un panel interno— consume recursos expuestos por un servidor 
según el dominio del dato. Esto aplica tanto para productos, stock y pedidos como para 
puntos, perfiles Maestro PYME, recomendaciones de servicio y encuestas. 
Las consultas de catálogo, productos, puntos visibles, perfiles de maestro y ciertos 
datos de stock pueden beneficiarse de estrategias de caché; en cambio, los cambios de estado, 
los pedidos, los pagos, las entregas, el uso de puntos y la encuesta postventa corresponden a 
operaciones de actualización o confirmación que deben gestionarse en tiempo oportuno. 
La información sensible incluye datos personales del cliente, credenciales de acceso, 
datos asociados al pago, historial de pedidos, cupos comerciales y condiciones de crédito. Si 
un servicio queda mal ubicado, se arriesga la duplicación de lógica, el quiebre de la 
arquitectura, el acoplamiento excesivo y la exposición insegura de información. Por ello, los 
servicios de crédito, puntos, pago e inventario deben ubicarse donde vive la lógica o el dato 
responsable. 
Encadenamiento de 
servicios en el flujo 
Servicio activado 
Respuesta que habilita el 
siguiente paso 
Consulta de catálogo 
WS_Productos 
Lista de productos disponible 
Validación de stock 
WS_Stock 
Stock suficiente o insuficiente 
Registro de pedido 
WS_Pedidos 
Pedido creado con identificador 
y estado inicial 
Confirmación de 
pago 
WS_Pagos 
Pago confirmado, pendiente o 
rechazado 
Preparación y 
seguimiento 
WS_EstadosPedido 
Cambio a en preparación / listo 
/ despachado 
Integración de Plataformas – ASY5131 
Cierre de entrega 
WS_Entrega 
FERREMAS | Evaluación Parcial 1 
Entrega confirmada y pedido 
cerrado 
Aplicación de puntos 
/ descuento 
WS_Puntos 
Descuento calculado o saldo 
actualizado 
Recomendación de 
servicio asociado 
Lista de Maestro PYME o 
servicio sugerido 
Registro de encuesta 
postventa 
WS_RecomendacionSe
rvicio 
WS_EncuestaSatisfacc
ion 
Encuesta almacenada y 
disponible para análisis 
Actualización 
automática de inventario tras 
pago 
WS_Pagos + 
WS_Stock 
Pago confirmado y stock 
ajustado 
8.5 Espacios para diagramas de arquitectura y servicios 
Figura 8. Diagrama de arquitectura por capas con ubicación de webservices 
Fuente: elaboración propia en Draw.io / diagrama del estudiante. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Figura 9. Mapa de servicios REST e interacción entre aplicaciones 
Fuente: elaboración propia en Draw.io/ diagrama del estudiante. 
9. Comparación As Is vs To Be 
Criterio 
As Is 
Canal de 
venta 
Principalment
e presencial 
To Be 
Impacto 
esperado 
Híbrido: tienda 
Mayor 
cobertura y 
continuidad 
+ web 
Visibilidad 
del pedido 
Baja 
Mejor 
experiencia y 
control 
Alta y basada 
en estados 
Coordinació
n entre áreas 
Manual / 
secuencial 
Menos 
fricción operativa 
Apoyada por 
servicios y flujos 
visibles 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
Integración de Plataformas – ASY5131 
Consulta de 
stock 
Interna y con 
intervención humana 
Disponible al 
proceso digital 
Mejor 
decisión de 
compra 
Medios de 
pago 
Tradicionales 
del flujo actual 
Débito, crédito 
y transferencia 
Más 
opciones para el 
cliente 
Trazabilidad Fragmentada Centralizada 
por estados y eventos 
Mejor 
control y auditoría 
Escalabilida
d 
Limitada por 
la tienda física 
Mayor, al 
incorporar canal web 
Expansión 
comercial 
Fidelización No existe 
esquema de puntos o 
descuentos digitales 
Puntos 
acumulables y 
descuentos por puntos 
Mayor 
recompra y 
vínculo con el 
cliente 
Servicios 
asociados 
No existe 
derivación 
estructurada a 
servicios 
Recomendació
n de Maestro PYME 
según compra 
Valor 
agregado y 
diferenciación 
Cliente 
Maestro PYME 
Sin 
tratamiento digital 
diferenciado 
Cuenta 
corriente, crédito y 
publicación/oferta de 
servicios 
Mejor 
segmentación 
comercial 
Postventa y 
satisfacción 
No existe 
encuesta digital 
estructurada 
Encuesta 
posterior a entrega o 
cierre 
Mejora 
continúa basada 
en datos 
Pago e 
inventario 
Relación no 
completamente 
automatizada 
Pago 
confirmado gatilla 
actualización de stock 
por webservices 
Coherenci
a entre venta, 
pago y bodega 
 
10. Matriz de cobertura de la pauta 
FERREMAS | Evaluación Parcial 1 
La siguiente matriz muestra de forma explícita cómo el presente informe cubre los 
puntos solicitados por la evaluación. Esta sección permite evidenciar de manera rápida que el 
documento aborda el modelo de negocio, los procesos involucrados, el BPMN del As Is, la 
propuesta To Be y la ubicación de los webservices. Además, el To Be incorpora mejoras 
funcionales reforzadas en clases: puntos, descuentos, encuesta de satisfacción, módulo 
Maestro PYME y actualización automática del inventario. 
Indicador de 
evaluación 
Cobertura en el informe 
Secciones / figuras 
asociadas 
Identifica el 
modelo de negocio 
Evalúa procesos 
para la integración 
Se describen negocio, 
problema, actores, procesos y 
clasificación. 
Secciones 4 y 5; 
Figura 1 
Se identifican cuatro 
procesos clave involucrados y su 
necesidad de integración. 
Se dejan espacios 
enumerados y justificados para 
diagramas As Is y To Be. 
Sección 5.3; 
Secciones 7 y 8 
Crea modelo 
BPMN del flujo actual y 
mejoras propuestas 
Define 
webservices y su 
ubicación según la 
arquitectura 
Figuras 2 a 7 
Se propone un conjunto de 
servicios, consumidores, 
expositores y capas afectadas. 
Sección 8; Figuras 8 
y 9 
11. Conclusiones 
El levantamiento del negocio de FERREMAS permite concluir que la empresa posee 
una estructura operativa clara, pero aún muy dependiente de la atención presencial. El proceso 
principal de venta está soportado por actividades de inventario, registro financiero y control 
administrativo, lo que evidencia una organización funcional, aunque limitada p or la falta de 
integración y por la ausencia de un canal digital. 
Integración de Plataformas – ASY5131 
FERREMAS | Evaluación Parcial 1 
El análisis del As Is confirma que la principal debilidad del negocio no es solamente 
tecnológica, sino también procesal: el flujo actual depende de múltiples traspasos secuenciales 
y de visibilidad reducida para el cliente y para las áreas internas. Esta situación justifica el 
diseño de un To Be basado en comercio electrónico, trazabilidad por estados y mejor 
articulación entre pedido, stock, pago, entrega y cierre. 
Finalmente, la propuesta de integración mediante webservices se alinea con la 
arquitectura por capas y con la necesidad de reutilizar la base operativa existente sin rehacer 
toda la infraestructura. En consecuencia, el informe entrega una base sólida para representar 
los diagramas BPMN, el mapa de procesos y la arquitectura de servicios, apuntando a un 
resultado consistente con las exigencias de la evaluación. 
12. Referencias 
1. Duoc UC. (2022). Evaluación Parcial 1: Análisis y Planificación – Caso 
FERREMAS [Material de cátedra]. Asignatura Integración de Plataformas, ASY5131. 
2. Duoc UC. (2022). Conociendo los procesos de negocio [Presentación de clase]. 
Asignatura Integración de Plataformas, ASY5131. 
3. Duoc UC. (2022). Identificando las capas de negocio [Presentación de clase]. 
Asignatura Integración de Plataformas, ASY5131. 
4. Duoc UC. (2022). Construyendo diagrama BPMN [Presentación de clase]. 
Asignatura Integración de Plataformas, ASY5131. 
5. Duoc UC. (2022). Webservices para la integración [Presentación de clase]. 
Asignatura Integración de Plataformas, ASY5131. 
Integración de Plataformas – ASY5131 