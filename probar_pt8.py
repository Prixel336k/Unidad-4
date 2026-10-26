from decimal import Decimal
from cargar_csv import load_fixture
from app.specifications import discount_rate

orders = load_fixture()

for order_id in ["O001", "O006", "O005", "O010"]:
    order = orders[order_id]
    rate = discount_rate(order)

    print(
        order_id,
        "Total:", order.total.amount,
        "Descuento:", rate * 100, "%"
    )