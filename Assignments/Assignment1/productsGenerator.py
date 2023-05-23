import random
from faker import Faker
fake = Faker()


#SELECT MAX(productCode) FROM classicmodel.products;    ---> TO find the max code of productCode so that the new ones can be unique 
# S72_3212

# Define lists of possible values for each attribute

start_num = 1
productCodes = ['S73_' + str(i) for i in range(1, 1000001)]
productNames = [fake.company() for i in range(1, 1000001)]
productLines = ['Motorcycles', 'Classic Cars', 'Planes', 'Ships', 'Trucks and Buses', 'Vintage Cars']
productScales = ['1:10', '1:12', '1:18', '1:24', '1:32', '1:50']
productVendors = [fake.company() for i in range(1, 1000001)]
productDescriptions = [fake.paragraph(nb_sentences=3) for i in range(1, 1000001)]
productStocks = [random.randint(0, 10000) for i in range(1000000)]
productPrices = [round(random.uniform(10.0, 500.0), 2) for i in range(1000000)]
MRSP = [round(random.uniform(100.0, 200.0), 2) for i in range(1000000)]

# print(len(productCodes))

# Open a file to write the SQL statements
with open('a1_load.sql', 'w') as f:
    # Loop over the lists and generate an INSERT statement for each record
    for i in range(1000000):
        f.write("INSERT INTO products (productCode, productName, productLine, productScale, productVendor, productDescription, quantityInStock, buyPrice, MSRP) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}');\n".format(
            productCodes[i], productNames[i], productLines[random.randint(0, 5)], productScales[random.randint(0, 5)], productVendors[random.randint(0, 99)], productDescriptions[i], int(productStocks[i]), productPrices[i], MRSP[i]))
