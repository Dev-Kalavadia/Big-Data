import mysql.connector
import monetdb.sql
import random
import time

# Define database connections
monet_conn = monetdb.sql.connect(database='flight', username='monetdb', password='monetdb', hostname='localhost', port=50000)
mysql_conn = mysql.connector.connect(database='flight', user='root', password='dk3936', host='localhost')

# Define queries
queries = [
    "SELECT count(*) from ontime",
    "SELECT avg(c1) FROM (SELECT YearD, MonthD, count(*) AS c1 FROM ontime WHERE YearD = %s GROUP BY YearD, MonthD) as tmp",
    "SELECT DayOfWeek, count(*) AS c FROM ontime WHERE YearD=2021 AND MonthD BETWEEN %s AND %s GROUP BY DayOfWeek ORDER BY c DESC",
    "SELECT Carrier, count(*) FROM ontime WHERE DepDelay>10 AND YearD=%s GROUP BY Carrier ORDER BY count(*) DESC",
    "SELECT DestCityName AS destination_city, count(DISTINCT OriginCityName) AS num_origins_of_flights FROM ontime WHERE YearD BETWEEN %s AND %s GROUP BY DestCityName ORDER BY 2 DESC LIMIT 10"
]

# Define function to execute queries
def execute_query(conn, query, args=None):
    start_time = time.time()
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    end_time = time.time()
    exec_time = end_time - start_time
    return exec_time

def generate_params(query):
    if "DayOfWeek" in query:
        return (random.randint(1, 6), random.randint(1, 6))
    elif "YearD" in query and "BETWEEN" in query:
        return (random.randint(2015, 2023), random.randint(2015, 2023))
    elif "YearD" in query:
        return (random.randint(2000, 2023),)  # return a tuple with one value
    else:
        return None


# Execute queries and collect execution times
for i, query in enumerate(queries):
    print(f"Query {i+1}: {query}")
    # Generate random parameters if needed
    params = generate_params(query)
    
    print(f"Parameters: {params}")
   
    # I coudlnt resolve the error that monetdb gave me for the cursors and number of values to unpack
    # try:
    #     monetdb_time = execute_query(monet_conn, query, params)
    #     print(f"MonetDB Execution Time: {monetdb_time:.4f} seconds")
    # except monetdb.sql.OperationalError as e:
    #     print(f"MonetDB Error: {e}")

        
    # Execute query on MySQL and collect execution time
    try:
        mysql_time = execute_query(mysql_conn, query, params)
        print(f"MySQL Execution Time: {mysql_time:.4f} seconds")
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    print("-" * 50)

# Close database connections
monet_conn.close()
