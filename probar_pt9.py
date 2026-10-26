from cargar_csv import load_fixture
from app.domain import InvalidOrderTransition

orders = load_fixture()
order = orders["O013"]

print("Estado inicial:", order.status)
print("Eventos iniciales:", len(order.events))

# Primera confirmacion
try:
    order.confirm()
    print("Primera confirmación:", order.status)
    print("Eventos:", [event.name for event in order.events])
except Exception as error:
    print("Error:", error)

# Segunda confirmacion
try:
    order.confirm()
except InvalidOrderTransition as error:
    print("Segunda confirmación rechazada:", error)

print("Estado final:", order.status)
print("Total de eventos:", len(order.events))
