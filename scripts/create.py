from absklep.models import Product, Property, Customer, Comment, Order, Employee, ProductAmount, Archival
from datetime import date, datetime
import re

import absklep

def get_data_file(data_file='data/customers.csv'):
    import os.path
    return os.path.join(os.path.dirname(__file__), data_file)

def create_customers(app):
    with open(get_data_file(),'r') as f:
        f.readline()
        line = f.readline()
        for i in range(480):
            customer = re.findall('([^"]*)(?:",|\n)', line)
            app.db.session.add(Customer(customer[9], customer[0]+customer[1]+'123'))
            line = f.readline()
        while line != '':
            employee = re.findall('([^"]*)(?:",|\n)', line)
            app.db.session.add(Employee(employee[0], employee[1], employee[9], employee[0]+employee[1]+'123', employee[8][:5]+employee[8][6:]))
            line = f.readline()
    app.db.session.commit()

if __name__ == '__main__':
    from sys import exit

    create_customers(absklep.app)

    exit(0)

