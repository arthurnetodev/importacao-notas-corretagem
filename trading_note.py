from order import Order
from typing import Dict

class TradingNote:
    def __init__(self, orders: Dict[str, Order], date):
        self.orders = orders
        self.date = date

    def __str__(self):
        orders_str = ""
        for key, value in self.orders.items():
            orders_str += key + "=" + str(value) + "\n"
        return f"Date: {self.date}\nOrders:\n{orders_str}"

