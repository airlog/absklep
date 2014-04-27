from absklep.models import Product, Property, Customer, Comment, Order, Employee, ProductAmount, Archival
from datetime import date, datetime
import re
import random

import absklep


def create_orders(app):
    customers = Customer.query.all()
    employees = Employee.query.all()
    products = Product.query.all()
        
    for i in range(300):
        c = random.randint(1,len(customers))
        if (random.randint(1,20) % 20 == 0):
            c = len(customers)         
        e = random.randint(1,len(employees))
        p = []
        order = Order()\
            .set_customer(c)\
            .set_firstname('imie')\
            .set_surname('nazwisko')\
            .set_payment_method(Order.ENUM_PAYMENT_METHODS_VALUES[random.randint(0,2)])\
            .set_address('Ulica 1/2')\
            .set_city('Miasto')\
            .set_postal_code('69-666')\

        max = random.randint(1,5)
        for k in range(max):
           order.add_product_amount(ProductAmount(random.randint(1,3)).set_product( products[ random.randint(0,len(products)-1) ] ))
            
        if (random.randint(1,10) % 10 > 0):
            order.set_employee(e)
            order.set_status(Order.ENUM_STATUS_VALUES[random.randint(0,3)])
        else:
            order.set_status(Order.ENUM_STATUS_VALUES[0])
        order.count_price()
        
        app.db.session.add(order)
        app.db.session.commit()             
        
if __name__ == '__main__':
    from sys import exit

    create_orders(absklep.app)

    exit(0)

