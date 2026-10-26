# TechStore U4 
## Estructura del proyecto

```
techstore-u4/
  datos/               CSV de clientes, productos, pedidos, detalle y escenarios
  cargar_csv.py        Carga los CSV y crea los objetos del dominio
  app/
    __init__.py
    domain.py          Money, Customer, OrderItem, Order, DomainEvent y excepciones
    specifications.py  Specification Pattern y reglas de descuento
    api.py             API REST con FastAPI
  tests/
    test_domain.py     Pruebas del dominio
    test_api.py        Pruebas de la API
  probar_pt8.py Verificaba que el punto estaba bien hecho mediante pruebas
  probar_pt9.py Verificaba que el punto estaba bien hecho mediante pruebas
  probar_pt10.py Verificaba que el punto estaba bien hecho mediante pruebas
  Bitacora_15escenarios.csv Bitacora creada desde probar_pt10.py para completar el punto 10
  evidencias/  Contiene imagenes de evidencias
    Carga_16pedidos.png
    Swagger_404.png
    Swagger_exito.png
    Swagger_422.png
    Swagger_409.png
```

## Instalación

Requiere Python 3.11 o superior.

1. Clonar el repositorio y entrar a la carpeta raíz del proyecto (la que contiene `cargar_csv.py`).
2. Crear y activar un entorno virtual:

```
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD:        .venv\Scripts\activate.bat
# macOS / Linux:      source .venv/bin/activate
```

3. Instalar las dependencias:

```
python -m pip install fastapi uvicorn pytest httpx
```

## Ejecución

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

**Cargar los datos** (debe mostrar los 16 pedidos en estado DRAFT):

```
python cargar_csv.py
```

**Levantar la API:**

```
uvicorn app.api:app --reload
```

- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
- Contrato OpenAPI: http://127.0.0.1:8000/openapi.json

Los pedidos se cargan al iniciar el servidor y viven en memoria. Para repetir una prueba desde cero, reinicia el servidor.

**Ejecutar las pruebas:**

```
python -m pytest -q
```

## Reglas de negocio

**Pedido (Order)**
- Solo un pedido en DRAFT admite artículos.
- El límite es de 20 unidades por pedido (suma de cantidades).
- Solo se admite la moneda MXN.
- Los montos usan `Decimal`; no pueden ser negativos.
- Cada artículo requiere un SKU no vacío y una cantidad mayor a cero.

**Descuentos** (implementados con Specifications combinadas con `&`, `|` y `~`)
- **10 %:** cliente VIP, total mayor a 500, al menos 4 unidades y sin promoción activa.
- **5 %:** total mayor a 5000 y sin promoción activa.
- Si se cumplen ambas reglas, se aplica primero el 10 %.
- Una promoción activa bloquea ambos descuentos.
- El umbral de 500 es estricto: un total exactamente igual a 500 no cumple.

## Estados y Domain Events

```
DRAFT --confirm--> CONFIRMED --ship--> SHIPPED --deliver--> DELIVERED
                       |                  |
                     cancel             return
                       |                  |
                   CANCELLED           RETURNED
```

| Operación | Estado requerido | Validación adicional | Evento |
|---|---|---|---|
| `confirm()` | DRAFT | Cliente activo y pedido con artículos | `OrderConfirmed` |
| `ship(tracking_number)` | CONFIRMED | Guía de envío no vacía | `OrderShipped` |
| `cancel(reason)` | CONFIRMED | Motivo no vacío | `OrderCancelled` |
| `deliver()` | SHIPPED | – | `OrderDelivered` |
| `return_order()` | SHIPPED | – | `OrderReturned` |

En todos los métodos se valida primero, después se cambia el estado y al final se registra el evento. Si una operación es inválida, el pedido no cambia y no se agrega ningún evento.

## Endpoints

| Método | Ruta | Cuerpo | Descripción |
|---|---|---|---|
| GET | `/orders/{id}` | – | Consulta un pedido (estado, unidades, total, artículos y eventos) |
| POST | `/orders/{id}/confirm` | – | Confirma un pedido |
| POST | `/orders/{id}/ship` | `{"tracking_number": "G123"}` | Envía un pedido confirmado |
| POST | `/orders/{id}/cancel` | `{"reason": "Motivo"}` | Cancela un pedido confirmado |

**Códigos de respuesta**

| Código | Cuándo ocurre | Ejemplo |
|---|---|---|
| 200 | La operación fue exitosa | Confirmar O013 por primera vez |
| 404 | El pedido no existe | Confirmar `X999` |
| 409 | Transición de estado no permitida | Confirmar O013 una segunda vez |
| 422 | Datos inválidos | Confirmar O007 (pedido sin artículos) |