from datetime import date, datetime
from hashlib import sha256
from os import urandom
from re import compile as Regex

from flask.ext.login import UserMixin

from absklep import app

db = app.db

LONG_TEXT = 4096 # e.g. description of product, text in comment
SHORT_TEXT = 128 # e.g. e-mail, address, city
VERY_SHORT_TEXT = 8 # e.g. apartment number

product_customer_assignment = db.Table(
    'ProductCustomer',
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
    db.Column('customer_id', db.Integer, db.ForeignKey('Customers.id'))
)

#product_order_assignment = db.Table(
#    'ProductOrder',
#    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
#    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'))
#)

#product_archival_assignment = db.Table(
#    'ProductArchival',
#    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
#    db.Column('archival_id', db.Integer, db.ForeignKey('Archivals.id'))
#)

product_property_assignment = db.Table(
    'ProductProperty',
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
    db.Column('property_id', db.Integer, db.ForeignKey('Properties.id'))
)


class Product(db.Model):

    __tablename__ = 'Products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(SHORT_TEXT), nullable = False)
    unit_price = db.Column(db.Integer, nullable=False)
    units_in_stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(LONG_TEXT))
    date_added = db.Column(db.DateTime, nullable=False)

    comments = db.relationship('Comment', cascade="all,delete", backref=db.backref('product'))
    properties = db.relationship('Property', cascade="all,delete", backref=db.backref('products'), secondary=product_property_assignment)

    def __init__(self, name, price, instock=0, description=None, date=None):
        if price < 0.0 or instock < 0:
            raise ValueError("invalid value")
        self.name, self.unit_price, self.units_in_stock, self.description = name, price, instock, description
        if date is None:
            date = datetime.now()
        self.date_added = date


class Comment(db.Model):

    RATE_ALLOWED_VALUES = [1, 2, 3, 4, 5]

    __tablename__ = 'Comments'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today())
    rate = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(LONG_TEXT))
    
    def __init__(self, pid, uid, rate, text, date=None):
        self.product_id, self.customer_id, self.date, self.rate, self.text = pid, uid, date, rate, text

    
class Customer(UserMixin, db.Model):

    __tablename__ = 'Customers'

    PASSWORD_LENGTH = 128   # 512 b = 64 B ==(base16)=> 128 B

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(SHORT_TEXT), unique=True, nullable=False)
    password = db.Column(db.String(PASSWORD_LENGTH), nullable=False)
    salt = db.Column(db.String(2*PASSWORD_LENGTH), nullable=False)

    comments = db.relationship('Comment', cascade="all,delete", backref=db.backref('customer'))
    orders = db.relationship('Order', cascade="all,delete", backref=db.backref('customer'))
    archivals = db.relationship('Archival', cascade="all,delete", backref=db.backref('customer'))
    observed = db.relationship('Product', cascade="all,delete", backref=db.backref('customers'), secondary=product_customer_assignment)

    @staticmethod
    def hash(pwd):
        return sha256(pwd).hexdigest()

    @staticmethod
    def generate_salt(length=PASSWORD_LENGTH):
        return urandom(length)

    @staticmethod
    def combine(salt, pwd):
        return salt + pwd.encode(encoding='UTF-8')

    def __init__(self, email, password, salt=None):
        if salt is None:
            salt = Customer.generate_salt()
        self.email, self.password, self.salt = email, Customer.hash(Customer.combine(salt, password)), ''.join(format(x, '02x') for x in salt)
        
    def verify_password(self, pwd):
        return self.password == Customer.hash(Customer.combine(bytes.fromhex(self.salt),pwd))
    
    def get_id(self):
        return 'u'+str(self.id)

        
class Property(db.Model):

    KEY_CATEGORY = 'Kategoria'

    __tablename__ = 'Properties'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(SHORT_TEXT))
    value = db.Column(db.String(SHORT_TEXT))

    @staticmethod
    def get_object_by_tuple(key, value):
        return Property\
            .query\
            .filter(Property.key == key, Property.value == value)\
            .first()

    def __init__(self, key, value):
        self.key, self.value = str(key), str(value)


class Employee(db.Model, UserMixin):

    __tablename__ = 'Employees'

    PASSWORD_LENGTH = 128   # 512 b = 64 B ==(base16)=> 128 B
    
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(SHORT_TEXT), nullable=False)
    surname = db.Column(db.String(SHORT_TEXT), nullable=False)
    email = db.Column(db.String(SHORT_TEXT), unique=True, nullable=False)
    password = db.Column(db.String(PASSWORD_LENGTH), nullable=False)
    salt = db.Column(db.String(2*PASSWORD_LENGTH), nullable=False)
    pesel = db.Column(db.String(11), unique=True, nullable=False)

    orders = db.relationship('Order', cascade="all,delete", backref=db.backref('employee'))
    archivals = db.relationship('Archival', cascade="all,delete", backref=db.backref('employee'))

    @staticmethod
    def hash(pwd):
        return sha256(pwd).hexdigest()

    @staticmethod
    def generate_salt(length=PASSWORD_LENGTH):
        return urandom(length)

    @staticmethod
    def combine(salt, pwd):
        return salt + pwd.encode(encoding='UTF-8')
        
    def verify_password(self, pwd):
        return self.password == Employee.hash(Employee.combine(bytes.fromhex(self.salt),pwd))

    def __init__(self, firstname, surname, email, password, pesel, salt=None):
        if salt is None:
            salt = Employee.generate_salt()
        self.email, self.password, self.salt = email, Employee.hash(Employee.combine(salt, password)), ''.join(format(x, '02x') for x in salt)
        self.firstname, self.surname, self.pesel = firstname, surname, pesel
    
    def get_id(self):
        return 'e'+str(self.id)
        
        
class ProductAmount(db.Model):

    __tablename__ = 'ProductAmounts'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')
    
    def __init__(self, amount=1):
        self.amount = amount
    
    def set_product(self, product):
        self.product = product
        return self
        

class Order(db.Model):

    __tablename__ = 'Orders'
    
    POSTAL_CODE_REGEX = Regex(r'(\d{2})-(\d{3})')
    ENUM_STATUS_VALUES = ['złożone', 'w przygotowaniu do wysłania', 'wysłane', 'anulowane']
    ENUM_PAYMENT_METHODS_VALUES = ['przelew', 'wysyłka za pobraniem', 'odbiór osobisty']
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employees.id'))
    date_ordered = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(*ENUM_STATUS_VALUES, name='s'), nullable=False)
    payment_method = db.Column(db.Enum(*ENUM_PAYMENT_METHODS_VALUES,name='t'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    firstname = db.Column(db.String(SHORT_TEXT), nullable=False)
    surname = db.Column(db.String(SHORT_TEXT), nullable=False)
    address = db.Column(db.String(SHORT_TEXT), nullable=False)
    city = db.Column(db.String(SHORT_TEXT), nullable=False)
    postal_code = db.Column(db.String(6), nullable=False)

#    products = db.relationship('Product', backref=db.backref('orders'), secondary=product_order_assignment)
    products_amount = db.relationship('ProductAmount', cascade="all,delete", backref=db.backref('order'))

    def __init__(self, d=date.today()):
        self.date_ordered = d

    def set_customer(self, customer):
        if isinstance(customer, Customer):
            customer = customer.id
        self.customer_id = customer
        return self

    def set_employee(self, employee):
        self.employee_id = employee
        return self
                
    def set_payment_method(self, mt):
        self.payment_method = mt
        return self

    def set_status(self, status):
        if status not in self.ENUM_STATUS_VALUES:
            raise ValueError("unsupported status value")
        self.status = status
        return self

    def set_price(self, price):
        self.price = price
        return self

    def set_firstname(self, name):
        self.firstname = name
        return self

    def set_surname(self, name):
        self.surname = name
        return self

    def set_address(self, addr):
        if not isinstance(addr, str):
            raise TypeError("a string expected")
        self.address = addr
        return self

    def set_city(self, city):
        if not isinstance(city, str):
            raise TypeError("a string expected")
        self.city = city
        return self

    def set_postal_code(self, code, regex=POSTAL_CODE_REGEX):
        if not isinstance(code, str):
            raise TypeError("postal code should be a string")
        if not regex.match(code):
            raise ValueError("postal code should match a regex '{}'".format(regex.pattern))
        self.postal_code = code
        return self

    def add_product_amount(self, product_amount):
        if not isinstance(product_amount, ProductAmount):
            raise TypeError("only products can be added to products list")
        self.products_amount.append(product_amount)
        return self

    def count_price(self, discount=None):
        """
        Count total price for order. Price is calculated by summing :unitPrice: fields of products contained in :products:
        field. Discount should be a value from 0.0 to 1.0, where 1.0 means 100% price and 0.3 means 30% of summed :unitPrice:.
        """
        if discount is None:
            discount = 1.0
        self.price = sum((p.amount * p.product.unit_price for p in self.products_amount)) * discount
        return self

    def done(self):
        pass



class ProductArchivalAmount(db.Model):

    __tablename__ = 'ProductArchivalAmounts'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    archival_id = db.Column(db.Integer, db.ForeignKey('Archivals.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')
    
    def __init__(self, amount=1):
        self.amount = amount
    
    def set_product(self, product_id):
        self.product_id = product_id
        return self

    def set_amount(self, amount):
        self.amount = amount
        return self

    def set_archival(self, archival_id):
        self.archival_id = archival_id
        return self


class Archival(db.Model):

    __tablename__ = 'Archivals'
    
    POSTAL_CODE_REGEX = Regex(r'(\d{2})-(\d{3})')
    ENUM_STATUS_VALUES = ['złożone', 'w przygotowaniu do wysłania', 'wysłane', 'anulowane']
    ENUM_PAYMENT_METHODS_VALUES = ['przelew', 'wysyłka za pobraniem', 'odbiór osobisty']

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employees.id'), nullable=False)
    date_ordered = db.Column(db.Date, nullable=False)
    date_archived= db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(*ENUM_STATUS_VALUES, name='u'), nullable=False)
    payment_method = db.Column(db.Enum(*ENUM_PAYMENT_METHODS_VALUES, name='v'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    firstname = db.Column(db.String(SHORT_TEXT), nullable=False)
    surname = db.Column(db.String(SHORT_TEXT), nullable=False)
    address = db.Column(db.String(SHORT_TEXT), nullable=False)
    city = db.Column(db.String(SHORT_TEXT), nullable=False)
    postal_code = db.Column(db.String(6), nullable=False)

#    products = db.relationship('Product', backref=db.backref('archivals'), secondary=product_archival_assignment)
    products_amount = db.relationship('ProductArchivalAmount', cascade="all,delete", backref=db.backref('archival'))
    
    def __init__(self, date=None):
        if date is None:
            date = datetime.now()
        self.date_archived = date

    def set_date_ordered(self, date):
        self.date_ordered = date
        return self
        
    def set_order_id(self, order_id):
        self.order_id = order_id
        return self
    
    def set_payment_method(self, mt):
        self.payment_method = mt
        return self

    def set_status(self, status):
        if status not in self.ENUM_STATUS_VALUES:
            raise ValueError("unsupported status value")
        self.status = status
        return self

    def set_price(self, price):
        self.price = price
        return self

    def set_firstname(self, name):
        self.firstname = name
        return self

    def set_surname(self, name):
        self.surname = name
        return self

    def set_address(self, addr):
        if not isinstance(addr, str):
            raise TypeError("a string expected")
        self.address = addr
        return self

    def set_city(self, city):
        if not isinstance(city, str):
            raise TypeError("a string expected")
        self.city = city
        return self

    def set_postal_code(self, code, regex=POSTAL_CODE_REGEX):
        if not isinstance(code, str):
            raise TypeError("postal code should be a string")
        if not regex.match(code):
            raise ValueError("postal code should match a regex '{}'".format(regex.pattern))
        self.postal_code = code
        return self

    def set_customer(self, customer_id ):
        self.customer_id = customer_id 
        return self
  
    def set_employee(self, employee_id ):
        self.employee_id = employee_id 
        return self
