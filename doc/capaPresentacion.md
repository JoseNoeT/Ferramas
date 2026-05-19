DOCUMENTO 1
Definición de la Capa de Presentación – Sistema FERREMAX
________________________________________
1. Introducción
El presente documento tiene como objetivo definir la capa de presentación del sistema FERREMAX, en el contexto de la implementación de una solución de comercio electrónico.
FERREMAX, actualmente, no cuenta con una plataforma de ventas en línea, lo que limita su capacidad de crecimiento y competitividad. Por ello, se propone el desarrollo de un sistema que permita la interacción digital entre clientes y los distintos actores internos de la empresa.
Este documento se enfoca específicamente en la capa de presentación, que corresponde a la interfaz gráfica del sistema.
________________________________________
2. Definición de la capa de presentación
La capa de presentación es la encargada de interactuar directamente con el usuario, permitiendo:
•	visualizar información del sistema 
•	ingresar datos mediante formularios 
•	navegar entre funcionalidades 
•	validar errores de formato 
Esta capa actúa como intermediaria entre el usuario y la capa de negocio, enviando solicitudes y mostrando respuestas de manera clara y amigable.
________________________________________
3. Objetivo de la capa de presentación
El objetivo de la capa de presentación es proporcionar una interfaz web intuitiva, accesible y funcional, que permita a los distintos actores del sistema FERREMAX interactuar eficientemente con la plataforma de comercio electrónico.
________________________________________
4. Actores del sistema
La interfaz debe considerar los siguientes tipos de usuarios:
•	Cliente: realiza compras en línea 
•	Vendedor: gestiona pedidos y coordina ventas 
•	Bodeguero: prepara pedidos 
•	Contador: valida pagos y registra entregas 
•	Administrador: supervisa el sistema y gestiona usuarios 
Cada actor tendrá acceso a funcionalidades específicas mediante interfaces diferenciadas.
________________________________________
5. Vistas del sistema (interfaz gráfica)
Se definen las siguientes vistas para la capa de presentación:
5.1 Vistas para cliente
•	Página de inicio (Home) 
•	Inicio de sesión (Login) 
•	Registro de usuario 
•	Catálogo de productos 
•	Detalle de producto 
•	Carrito de compras 
•	Proceso de compra (Checkout) 
•	Confirmación de compra 
5.2 Vistas para usuarios internos
•	Panel de vendedor 
•	Panel de bodeguero 
•	Panel de contador 
•	Panel de administrador 
________________________________________
6. Flujo principal del sistema
El flujo principal de interacción para el cliente es el siguiente:
Home → Login/Registro → Catálogo → Carrito → Checkout → Confirmación
Este flujo representa el proceso de compra dentro del sistema de comercio electrónico.
________________________________________
7. Requisitos de la interfaz
La capa de presentación debe cumplir con los siguientes requisitos:
•	Interfaz amigable e intuitiva 
•	Navegación clara entre vistas 
•	Validación de datos en formularios (frontend) 
•	Acceso mediante autenticación de usuarios 
•	Adaptación a múltiples roles 
•	Visualización clara de productos y pedidos 
•	Interacción mediante botones y formularios 
________________________________________
8. Arquitectura del frontend
La implementación de la capa de presentación se realizará utilizando tecnologías web estándar:
•	HTML (estructura) 
•	CSS (diseño visual) 
•	JavaScript (interacción y validaciones) 
Estructura del proyecto:
ferremax-frontend/
│── index.html
│── login.html
│── registro.html
│── catalogo.html
│── producto.html
│── carrito.html
│── checkout.html
│── Panel-vendedor.html
│── Panel-bodeguero.html
│── Panel-contador.html
│── /css
│    └── styles.css
│── /js
│    └── app.js
│── /img
________________________________________
9. Justificación
La definición de la capa de presentación se basa en los requerimientos del caso FERREMAX, permitiendo representar el proceso de comercio electrónico y la interacción de múltiples actores dentro del sistema.
Esta capa es fundamental, ya que constituye el punto de contacto entre el usuario y la plataforma, facilitando la ejecución de los procesos del negocio de manera eficiente.
________________________________________
10. Conclusión
La capa de presentación del sistema FERREMAX establece la base para la interacción del usuario con la plataforma, permitiendo estructurar de manera clara las funcionalidades del sistema antes de su implementación técnica.
Su correcta definición asegura que el sistema sea usable, escalable y alineado con las necesidades del negocio.

