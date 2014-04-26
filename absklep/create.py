from .models import Product, Property, Customer, Comment, Order, Employee, ProductAmount, Archival
from datetime import date, datetime
import re


def load_database(app):
    app.db.drop_all()
    app.db.create_all()
    with open('absklep/data/customers.csv','r') as f:
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
    
