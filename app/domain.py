from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone

class DomainException(Exception): pass
class InvalidOrderData(DomainException): pass
class InvalidOrderTransition(DomainException): pass
class OrderItemLimitExceeded(DomainException): pass

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self):
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("Monto inválido")

    def add(self, other):
        if self.currency != other.currency:
            raise InvalidOrderData("Monedas distintas")
        return Money(self.amount + other.amount, self.currency)

@dataclass(frozen=True)
class Customer:
    id: str
    vip: bool = False
    active: bool = True

@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("Artículo inválido")

    @property
    def subtotal(self):
        return Money(self.unit_price.amount * self.quantity)

class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

@dataclass(frozen=True)
class DomainEvent:
    name: str
    order_id: str
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

@dataclass
class Order:
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = field(default_factory=list)
    events: list = field(default_factory=list)

    def __post_init__(self):
        if self.customer.vip:
            self.has_promotion = True

    @property
    def units(self):
        return sum(item.quantity for item in self.items)

    @property
    def total(self):
        amount = sum((x.subtotal.amount for x in self.items), Decimal("0"))
        return Money(amount)

    def add_item(self, item):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo DRAFT admite artículos")
        if self.units + item.quantity > 20:
            raise OrderItemLimitExceeded("Máximo 20 unidades")
        if item.unit_price.currency != "MXN":
            raise InvalidOrderData("Solo MXN")
        
        self.items.append(item)
        
        if self.units >= 10:
            self.has_promotion = True

    def confirm(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo DRAFT puede confirmarse")
        if not self.customer.active:
            raise InvalidOrderData("El cliente está inactivo")
        if not self.items:
            raise InvalidOrderData("El pedido requiere artículos")

        self.status = OrderStatus.CONFIRMED
        self.events.append(DomainEvent("OrderConfirmed", self.id))

    def ship(self, tracking_number):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo CONFIRMED puede enviarse")
        if not tracking_number or not tracking_number.strip():
            raise InvalidOrderData("Se requiere una guía de envío")

        self.status = OrderStatus.SHIPPED
        self.events.append(DomainEvent("OrderShipped", self.id))

    def cancel(self, reason):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo CONFIRMED puede cancelarse")
        if not reason or not reason.strip():
            raise InvalidOrderData("Se requiere un motivo de cancelación")

        self.status = OrderStatus.CANCELLED
        self.events.append(DomainEvent("OrderCancelled", self.id))

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo SHIPPED puede marcarse como entregado")

        self.status = OrderStatus.DELIVERED
        self.events.append(DomainEvent("OrderDelivered", self.id))

    def return_order(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo SHIPPED puede devolverse")

        self.status = OrderStatus.RETURNED
        self.events.append(DomainEvent("OrderReturned", self.id))
