TECHSTORE U4 - PAQUETE DEL ALUMNO

OBJETIVO: usar datos reproducibles para la Actividad 4 de CLN.

CONTENIDO
 datos/clientes.csv: 12 clientes (es_vip y activo: 1=si, 0=no).
 datos/productos.csv: 12 productos (precio_mxn en formato decimal).
 datos/pedidos.csv: 16 pedidos, todos inicialmente DRAFT.
 datos/detalle_pedidos.csv: 21 lineas de articulos.
 datos/escenarios.csv: 15 situaciones de evaluacion. La columna objetivo contiene solo el tipo general de resultado, no la resolucion numerica.
 cargar_csv.py: convierte los CSV a objetos Order del proyecto de referencia.

USO
 1. Crea tu proyecto de la Actividad 4 (Python 3.11+, FastAPI y pytest).
 2. Copia cargar_csv.py y la carpeta datos/ a la raiz del proyecto, junto a app/.
 3. Ejecuta python cargar_csv.py. Si usas tu propio modelo, adapta los nombres de clases y parametros del cargador.
 4. Implementa y ejecuta los escenarios E01 a E15.
 5. Documenta para cada escenario: precondiciones, operacion, resultado, evento y prueba.
 6. No cambies las reglas de la Actividad 4 para que un caso pase.

REGLAS DIDACTICAS
 - Money no admite importes negativos; usar Decimal, no float.
 - Maximo 20 unidades por pedido (no 20 lineas).
 - Descuento 10%: cliente VIP, total >500 MXN, >=4 unidades, sin promocion.
 - Descuento 5%: total >5000 MXN, sin promocion. Prioridad 10% si ambas condiciones se cumplen.
 - Todos los pedidos empiezan DRAFT para que la maquina de estados sea ejecutada por el alumno.
 - El stock de productos es contexto de catalogo: no se implementa control de inventario en el dominio de este laboratorio.
 - El repositorio en memoria no persiste cambios entre ejecuciones.

ADVERTENCIA
 No entregamos la base SQLite en el paquete del alumno: la persistencia es opcional y no debe desplazar el objetivo de reglas y transiciones.
