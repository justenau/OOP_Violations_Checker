from random import random
from enum import Enum

# Should raise warning for LCOM
class Store:
    def __init__(self, address, title):
        self.address = address
        self.title = title
        self.workers = []
        self.manager = None
        self.products = []
        self.cash_total = 0

    def add_product(self, name, cost, qty=1):
        product = Product(name,cost,qty)
        self.products.append(product)

    def remove_product(self, product, qty=1):
        if product.is_in_stock(qty):
            if product.quantity == qty:
                self.products.remove(product)
            else:
                product.quantity -= qty
        else:
            raise Exception('There\'s no products to remove')

    def add_worker(self, name, salary, position):
        worker = Worker(name, salary, position)
        self.workers.append(worker)

    def remove_worker(self, worker):
        self.workers.remove(worker)

    def sell_product(self, product, worker, qty=1):
        if not product.is_in_stock(qty):
            raise Exception('Product not in stock!')
        sum = product.calculateCost(qty)
        worker.sales_total += sum
        product.quantity -= sum

class Product:
    def __init__(self, name, cost, quantity=0):
        self.name = name
        self.cost = cost
        self.quantity = quantity

    def calculate_cost(self, qty):
        return qty * self.cost if self.is_in_stock(qty) else 0

    def is_in_stock(self, qty):
        return qty >= self.quantity


class Worker:
    def __init__(self, name, salary, position):
        self.name = name
        self.salary = salary
        self.position = position
        self.sales_total = 0
        self.is_manager = False

    # Should raise warning for CCM
    def should_get_raise(self):
        if self.sales_total > 1000:
            if not self.is_manager:
                return True
            else:
                return False
        elif self.sales_total > 800:
            if self.position == Position.BEGINNER:
                if self.salary > 600:
                    return False
                elif self.sales_total < 1000:
                    return True
                else:
                    return False
            elif self.sales_total > 3000:
                return True
            else:
                return False
        elif self.sales_total > 500:
            if self.salary < 500 and self.position == Position.BEGINNER:
                return True

        random_luck = random.randint(0, 1)
        if random_luck == 1:
            return True
        else:
            return False

class Position(Enum):
    BEGINNER=1
    EXPERIENCED=2
    HEAD_OF_SALES=3