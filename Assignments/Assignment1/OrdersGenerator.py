import random
import datetime
import mysql.connector
from faker import Faker
fake = Faker()

# establish database connection
cnx = mysql.connector.connect(user='root', password='Dk3936',
                              host='localhost', database='classicmodel')
cursor = cnx.cursor()

# get the maximum orderNumber from the orders table
# To make sure that orderNumber is unique 
cursor.execute("SELECT MAX(orderNumber) FROM orders")
max_order_number = cursor.fetchone()[0] or 0

# generate 100 random orders
for i in range(1, 100):
    # generate a unique orderNumber for the new order
    order_number = max_order_number + i

    # select a random customerNumber
    cursor.execute("SELECT customerNumber FROM customers ORDER BY RAND() LIMIT 1")
    customer_number = cursor.fetchone()[0]

    # generate a random orderDate between 2018-01-01 and 2023-02-18
    start_date = datetime.date(2018, 1, 1)
    end_date = datetime.date(2023, 2, 18)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    order_date = start_date + datetime.timedelta(days=random_days)

    # generate a random requiredDate 10 days after the orderDate
    required_date = order_date + datetime.timedelta(days=10)

    # generate a random shippedDate between the orderDate and requiredDate
    shipped_date = order_date + datetime.timedelta(days=random.randint(1, 10))

    # generate a random status
    status_options = ['Shipped', 'On Hold', 'Cancelled']
    status = random.choice(status_options)

    # insert the new order into the orders table
    add_order = ("INSERT INTO orders "
                 "(orderNumber, orderDate, requiredDate, shippedDate, status, customerNumber) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
    order_data = (order_number, order_date, required_date, shipped_date, status, customer_number)
    cursor.execute(add_order, order_data)

    # select a random productCode and generate a random quantity for the order details
    cursor.execute("SELECT productCode, quantityInStock, MSRP FROM products ORDER BY RAND() LIMIT 1")
    product_code, quantity_in_stock, MSRP = cursor.fetchone()
    order_quantity = random.randint(1, min(10, quantity_in_stock))
    orderLineNo = random.randint(1, 10)

    # insert the new order detail into the orderdetails table
    add_order_detail = ("INSERT INTO orderdetails "
                        "(orderNumber, productCode, quantityOrdered, priceEach, orderLineNumber) "
                        "VALUES (%s, %s, %s, %s, %s)")
    order_detail_data = (order_number, product_code, order_quantity, MSRP, orderLineNo)
    cursor.execute(add_order_detail, order_detail_data)

# commit the changes and close the database connection
cnx.commit()
cursor.close()
cnx.close()
