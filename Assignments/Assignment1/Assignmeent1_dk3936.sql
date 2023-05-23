/* show table status from classicmodel; */

/* Part 3.1 */
SELECT * FROM classicmodel.customers;
/* Part 3.2 */
SELECT orderNumber, orderDate, status FROM classicmodel.orders WHERE status='In Process';
/* Part 3.3 */
SELECT COUNT(*) FROM classicmodel.products;
/* Part 3.4 */
SELECT MAX(creditLimit), MIN(creditLimit), AVG(creditLimit) FROM classicmodel.customers;

/* Part 3.5 */
SELECT c.customerName, o.orderNumber, SUM(od.quantityOrdered * od.priceEach) AS totalCost
FROM classicmodel.customers c
JOIN classicmodel.orders o ON c.customerNumber = o.customerNumber
JOIN classicmodel.orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY o.orderNumber;

/* Part 3.6 */
SELECT c.customerName
FROM classicmodel.customers c
JOIN classicmodel.orders o ON c.customerNumber = o.customerNumber
GROUP BY c.customerNumber
HAVING COUNT(o.orderNumber) > 5;

/* Part 3.7 */
SELECT o.*
FROM classicmodel.orders o
JOIN classicmodel.customers c ON o.customerNumber = c.customerNumber
WHERE c.creditLimit > 200000;

/* Part 3.8 */

SELECT DISTINCT orderdetails.orderNumber
FROM classicmodel.orderdetails
JOIN classicmodel.products ON orderdetails.productCode = products.productCode
WHERE products.quantityInStock >= 8000;


EXPLAIN ANALYZE SELECT DISTINCT orderdetails.orderNumber
FROM classicmodel.orderdetails
JOIN classicmodel.products ON orderdetails.productCode = products.productCode
WHERE products.quantityInStock >= 8000;


CREATE INDEX idx_orderdetails_productCodeNo ON classicmodel.orderdetails (productCode);
CREATE INDEX idx_products_quantityInStock ON classicmodel.products (quantityInStock);

ALTER TABLE classicmodel.orderdetails
ADD INDEX idx_orderdetails_products (productCode, quantityInStock);

EXPLAIN ANALYZE SELECT DISTINCT orderdetails.orderNumber
FROM classicmodel.orderdetails
JOIN classicmodel.products ON orderdetails.productCode = products.productCode
WHERE products.quantityInStock >= 8000;

/* Additional queries to test the execution time for returning the product Name and Vendor of products with at least 8,000 items in stock */
EXPLAIN ANALYZE SELECT DISTINCT products.productName, products.productVendor, orderdetails.orderNumber
FROM classicmodel.orderdetails
JOIN classicmodel.products ON orderdetails.productCode = products.productCode
WHERE products.quantityInStock >= 8000
GROUP BY products.productName, products.productVendor, orderdetails.orderNumber;

/* Additional queries to test the execution time for returning order numbers of products between the range 100 - 3000 items in stock */
EXPLAIN ANALYZE SELECT DISTINCT orderdetails.orderNumber
FROM classicmodel.orderdetails
JOIN classicmodel.products ON orderdetails.productCode = products.productCode
WHERE products.quantityInStock BETWEEN 100 AND 3000;


/*
SHOW CREATE DATABASE classicmodel;
DROP INDEX priceEach_idx ON classicmodel.orderdetails;
DROP INDEX idx_orderdetails_productCodeNo ON classicmodel.orderdetails;*/






