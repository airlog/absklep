import re
from datetime import date, datetime, timedelta
import random

import absklep
from absklep.models import Customer, Employee, Order, ProductAmount, Product, ProductArchivalAmount, Archival



def gen_archived(app):
    emp_count = app.db.session.query(Employee).count()
    cust_count = app.db.session.query(Customer).count()
    prod_count = app.db.session.query(Product).count()
    for i in range(1000):
        #losowa data w ostatnim roku i status
        order = Archival(datetime.now() - timedelta( days=random.randint(20,365), hours=random.randint(0,23), minutes=random.randint(0,59)))
        order.set_date_ordered(order.date_archived - timedelta(days=3))\
             .set_order_id(1)\
             .set_employee ( random.randrange(1, emp_count) )\
             .set_customer ( random.randrange(1, cust_count) )
             
        order.set_firstname("Andy")\
            .set_surname("Lloyd")\
            .set_address("Thames")\
            .set_city("London")\
            .set_postal_code("12-345")\
            .set_payment_method(Order.ENUM_PAYMENT_METHODS_VALUES[0])\
            .set_price(random.random() * 12000)\
            .set_status('wysłane')
        
        for j in range(random.randrange(1,10)): 
            order.products_amount.append(ProductArchivalAmount(random.randint(1,14)).set_product(random.randrange(1, prod_count)))
        app.db.session.add(order)
        app.db.session.commit()
    
if __name__ == '__main__':
    gen_archived(absklep.app)
