
import csv
from decimal import Decimal

from cargar_csv import load_fixture, rows
from app.domain import (
    Money,
    OrderItem,
    InvalidOrderData,
    InvalidOrderTransition,
    OrderItemLimitExceeded,
)
from app.specifications import discount_rate


resultados = []


def estado(order):
    return order.status.value


def registrar(caso, inicial, operacion, resultado, explicacion):
    resultados.append({
        "caso_id": caso,
        "estado_inicial": inicial,
        "operacion": operacion,
        "resultado_real": resultado,
        "explicacion": explicacion,
    })


def ejecutar(order, descripcion, funcion):
    #Ejecuta una operación y registra su resultado y sus eventos.
    eventos_antes = len(order.events)

    try:
        funcion()
        resultado = f"Éxito; estado actual: {estado(order)}"
    except (
        InvalidOrderData,
        InvalidOrderTransition,
        OrderItemLimitExceeded,
    ) as error:
        resultado = f"Rechazo: {error}"

    eventos_nuevos = [
        evento.name for evento in order.events[eventos_antes:]
    ]

    if eventos_nuevos:
        eventos = ", ".join(eventos_nuevos)
    else:
        eventos = "ninguno"

    return f"{descripcion}: {resultado}. Eventos nuevos: {eventos}."


def nuevo_pedido(pedido_id):
    # Cada escenario comienza con los datos originales.
    return load_fixture()[pedido_id]


def registrar_descuento(caso, pedido_id, esperado, explicacion):
    order = nuevo_pedido(pedido_id)
    inicial = estado(order)
    descuento = discount_rate(order)
    real = f"{descuento * 100}%"

    registrar(
        caso,
        inicial,
        "Evaluar descuento",
        real,
        f"{explicacion}. Esperado: {esperado}. "
        "La evaluación no cambia el pedido ni genera eventos.",
    )


# E01: descuento del 10 %
registrar_descuento(
    "E01", "O001", "10%",
    "Regla VIP, monto mayor a 500, al menos 4 unidades y sin promoción"
)

# E02: sin descuento
registrar_descuento(
    "E02", "O002", "0%",
    "Cliente no VIP y total menor a 5000, según el escenario"
)

# E03: cliente inactivo
order = nuevo_pedido("O003")
inicial = estado(order)
detalle = ejecutar(order, "Confirmar", order.confirm)
registrar(
    "E03", inicial, "Confirmar", detalle,
    "Se espera rechazo por cliente inactivo. "
    f"Estado final: {estado(order)}."
)

# E04: la promocion bloquea el descuento
registrar_descuento(
    "E04", "O005", "0%",
    "La promocion activa impide aplicar ambos descuentos"
)

# E05: descuento del 5 %
registrar_descuento(
    "E05", "O006", "5%",
    "Total mayor a 5000 y sin promocion"
)

# E06: pedido sin articulos
order = nuevo_pedido("O007")
inicial = estado(order)
detalle = ejecutar(order, "Confirmar", order.confirm)
registrar(
    "E06", inicial, "Confirmar", detalle,
    "Se espera rechazo porque el pedido no tiene articulos. "
    f"Estado final: {estado(order)}."
)

# E07: pedido con 20 unidades
order = nuevo_pedido("O008")
inicial = estado(order)
unidades = order.units
detalle = ejecutar(order, "Confirmar", order.confirm)
registrar(
    "E07", inicial, "Confirmar", detalle,
    f"Unidades iniciales: {unidades}. El limite permitido es 20. "
    f"Estado final: {estado(order)}."
)

# E08: intentar agregar 2 unidades y exceder el limite
order = nuevo_pedido("O009")
inicial = estado(order)

productos = {
    fila["sku"]: Decimal(fila["precio_mxn"])
    for fila in rows("productos.csv")
}
precio = productos["SKU003"]

detalle = ejecutar(
    order,
    "Agregar SKU003 x2",
    lambda: order.add_item(
        OrderItem("SKU003", 2, Money(precio))
    ),
)

registrar(
    "E08", inicial, "Agregar SKU003 x2", detalle,
    f"Unidades antes: {order.units}. Se intenta agregar 2 unidades. "
    f"Unidades despues: {order.units}. Se espera rechazo si se exceden 20."
)

# E09: el umbral es estricto: total > 500
registrar_descuento(
    "E09", "O010", "0%",
    "Un total exactamente igual a 500 no supera el umbral"
)

# E10: solo 3 unidades
registrar_descuento(
    "E10", "O011", "0%",
    "La regla del 10% exige al menos 4 unidades"
)

# E11: confirmar si, enviar sin guia no
order = nuevo_pedido("O012")
inicial = estado(order)
pasos = []

pasos.append(ejecutar(order, "Confirmar", order.confirm))
pasos.append(
    ejecutar(order, "Enviar sin guia", lambda: order.ship(""))
)

registrar(
    "E11", inicial, "Confirmar y enviar sin guia",
    " | ".join(pasos),
    f"La confirmación debe ser valida y el envio rechazado por falta de guia. "
    f"Estado final: {estado(order)}."
)

# E12: confirmar dos veces
order = nuevo_pedido("O013")
inicial = estado(order)
pasos = []

pasos.append(ejecutar(order, "Primera confirmacion", order.confirm))
pasos.append(ejecutar(order, "Segunda confirmacion", order.confirm))

registrar(
    "E12", inicial, "Confirmar dos veces",
    " | ".join(pasos),
    f"La segunda confirmacion debe rechazarse. Estado final: {estado(order)}."
)

# E13: cancelar despues de enviar
order = nuevo_pedido("O014")
inicial = estado(order)
pasos = []

pasos.append(ejecutar(order, "Confirmar", order.confirm))
pasos.append(
    ejecutar(order, "Enviar", lambda: order.ship("GUIA-001"))
)
pasos.append(
    ejecutar(order, "Cancelar", lambda: order.cancel("Cancelacion de prueba"))
)

registrar(
    "E13", inicial, "Confirmar, enviar y cancelar",
    " | ".join(pasos),
    f"La cancelacion debe rechazarse en SHIPPED. Estado final: {estado(order)}."
)

# E14: devolver pedido enviado
order = nuevo_pedido("O015")
inicial = estado(order)
pasos = []

pasos.append(ejecutar(order, "Confirmar", order.confirm))
pasos.append(
    ejecutar(order, "Enviar", lambda: order.ship("GUIA-002"))
)
pasos.append(ejecutar(order, "Devolver", order.return_order))

registrar(
    "E14", inicial, "Confirmar, enviar y devolver",
    " | ".join(pasos),
    f"Se espera terminar en RETURNED. Estado final: {estado(order)}."
)

# E15: entregar pedido enviado
order = nuevo_pedido("O016")
inicial = estado(order)
pasos = []

pasos.append(ejecutar(order, "Confirmar", order.confirm))
pasos.append(
    ejecutar(order, "Enviar", lambda: order.ship("GUIA-003"))
)
pasos.append(ejecutar(order, "Entregar", order.deliver))

registrar(
    "E15", inicial, "Confirmar, enviar y entregar",
    " | ".join(pasos),
    f"Se espera terminar en DELIVERED. Estado final: {estado(order)}."
)


# Mostrar los resultados en pantalla
for resultado in resultados:
    print("-" * 80)
    for columna, valor in resultado.items():
        print(f"{columna}: {valor}")


# Guardar el registro en CSV
with open(
    "resultados_pt10.csv",
    "w",
    newline="",
    encoding="utf-8-sig",
) as archivo:
    columnas = [
        "caso_id",
        "estado_inicial",
        "operacion",
        "resultado_real",
        "explicacion",
    ]
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows(resultados)

print("\nSe guardo todo en resultados_pt10.csv")
