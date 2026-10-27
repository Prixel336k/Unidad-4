import pytest
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import Order, Customer, OrderItem, Money, OrderItemLimitExceeded, InvalidOrderData, InvalidOrderTransition
from app.specifications import discount_rate

def test_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))

def test_pedido_o001_inicia_draft():
    orders = load_fixture()
    assert orders["O001"].status.value == "DRAFT"
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")

def test_limite_20_unidades_por_pedido():
    cliente = Customer(id="C01", active=True)
    pedido = Order(id="0001", customer=cliente)
    pedido.add_item(OrderItem(sku="SKU1", quantity=15, unit_price=Money(Decimal("100.00"))))
    with pytest.raises(OrderItemLimitExceeded): 
        pedido.add_item(OrderItem(sku="SKU2", quantity=6, unit_price=Money(Decimal("50.00"))))

def test_cliente_inactivo():
    cliente = Customer(id="C02", active=False)
    pedido = Order(id="0002", customer=cliente)
    with pytest.raises(InvalidOrderData):
        pedido.confirm()

def test_pedido_vacio_no_se_confirma():
    cliente = Customer(id="C03", active=True)
    pedido = Order(id="0003", customer=cliente)
    with pytest.raises(InvalidOrderData):
        pedido.confirm()

def test_descuento_vip():
    # Preparar datos: is_vip=True, sin promoción, 4 unidades, total > 500
    cliente = Customer(id="C_VIP", is_vip=True, active=True)
    pedido = Order(id="0004", customer=cliente, has_promotion=False)
    pedido.add_item(OrderItem(sku="SKU_VIP", quantity=4, unit_price=Money(Decimal("150.00"))))
    
    # Ejecutar y comprobar
    assert discount_rate(pedido) == Decimal("0.10")

def test_promocion_activa():
    # Preparar datos: is_vip=True, CON promoción, 4 unidades
    cliente = Customer(id="C_PROM", is_vip=True, active=True)
    pedido = Order(id="0005", customer=cliente, has_promotion=True)
    pedido.add_item(OrderItem(sku="SKU_PROM", quantity=4, unit_price=Money(Decimal("150.00"))))
    
    # Ejecutar y comprobar
    assert discount_rate(pedido) == Decimal("0.00")

def test_cancelacion_desde_shipped():
    cliente = Customer(id="C05", active=True)
    pedido = Order(id="0006", customer=cliente)
    pedido.add_item(OrderItem(sku="SKU1", quantity=1, unit_price=Money(Decimal("100.00"))))
    pedido.confirm()
    pedido.ship("TRACK123")
    with pytest.raises(InvalidOrderTransition):
        pedido.cancel("Ya no lo quiero")
