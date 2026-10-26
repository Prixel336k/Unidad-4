"""Carga fixtures TechStore desde CSV en objetos del dominio de U4.
Ejecutar desde la carpeta que contiene 'datos' y este archivo.
"""
import csv
from pathlib import Path
from decimal import Decimal
from app.domain import Customer, Order, OrderItem, Money

BASE = Path(__file__).resolve().parent / "datos"

def rows(filename):
    with (BASE / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def load_fixture():
    clients = {
        x["cliente_id"]: Customer(
            x["cliente_id"], bool(int(x["es_vip"])), bool(int(x["activo"]))
        ) for x in rows("clientes.csv")
    }
    prices = {x["sku"]: Decimal(x["precio_mxn"]) for x in rows("productos.csv")}
    orders = {
        x["pedido_id"]: Order(
            customer=clients[x["cliente_id"]],
            id=x["pedido_id"],
            has_promotion=bool(int(x["tiene_promocion"]))
        ) for x in rows("pedidos.csv")
    }
    for x in rows("detalle_pedidos.csv"):
        orders[x["pedido_id"]].add_item(
            OrderItem(x["sku"], int(x["cantidad"]), Money(prices[x["sku"]]))
        )
    return orders

if __name__ == "__main__":
    orders = load_fixture()
    for order_id, order in orders.items():
        print(order_id, order.status.value, order.units, order.total.amount)
