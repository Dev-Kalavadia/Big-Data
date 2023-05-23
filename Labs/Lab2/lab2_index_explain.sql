/*
Lab 2 Big Data Systems 2023
Credit: Sample retailer data adapted from http://www.mysqltutorial.org/mysql-sample-database.aspx
Warning: The schema is different!
*/

select * from orderdetails;
explain analyze select * from orderdetails; # notice how the table is scanned.
explain analyze select orderNumber from orderdetails; # how about now? why? 
explain analyze select orderNumber, productCode from orderdetails;

# Table or index ?
select * from orderdetails where orderNumber = 10420;
explain analyze select * from orderdetails where orderNumber > 10420;


# Table or index ?
explain analyze select * from orderdetails where priceEach >1;
create index priceEach_idx ON orderdetails (priceEach);
explain analyze select * from orderdetails where priceEach >1;
explain analyze select * from orderdetails where priceEach >197 and priceEach <201;