#Assingment5 Spark Practice
#Dev Kalavadiya - dk3936

#Loading the dataset into the dataframe
titanic_df = spark.read.csv("titanic.csv", header=True, inferSchema=True)
titanic_df.show(5)

# 1.Count and retrieve 10 passengers who survived.
survived_count = titanic_df.filter(titanic_df.Survived == 1).count()
print("Number of passengers who survived: ", survived_count)

titanic_df.filter(titanic_df.Survived == 1).limit(10).show()

# 2.Add a column called "IsChild" that contains "True" if the passenger's age is less than 18, and "False" otherwise.
from pyspark.sql.functions import when

titanic_df = titanic_df.withColumn("IsChild", when(titanic_df.Age < 18, True).otherwise(False))
titanic_df.show(10)

# 3. Group the DataFrame by the "Pclass" (Ticket class) column and count the number of passengers in each class.
titanic_df.groupBy("Pclass").count().show()

# 4. Rename the "Pclass" column to "PassengerClass" using the alias function
from pyspark.sql.functions import col
    # Since this is a selection only one coloumn is projected and retunred with the name change
    # titanic_df = titanic_df.select(col("Pclass").alias("PassengerClass"))

# Changing the alias of the Pclass and the rest have the same column name and redefining the titanic_df
titanic_df = titanic_df.select(col("PassengerId"), col("Survived"), col("Pclass").alias("PassengerClass"), col("Name"), col("Sex"), col("Age"), col("SibSp"), col("Parch"), col("Ticket"), col("Fare"), col("Cabin"), col("Embarked"), col("IsChild"))
titanic_df.show(10)

    # Easier and Simpler way
titanic_df = titanic_df.withColumnRenamed("Pclass", "PassengerClass")

# 5. Sort the DataFrame by the "Age" column in descending order.
from pyspark.sql.functions import desc

titanic_df = titanic_df.sort(desc("Age"))
titanic_df.show(10)

# 6. Calculate the average age of passengers in each passenger class using the groupBy and agg functions.
titanic_df.groupBy("PassengerClass").agg({"Age": "average"}).show()

# 7. Find the top 5 passengers with the highest fare.
titanic_df.sort(desc("Fare")).limit(5).show()

# 8. Create a new DataFrame that contains the total fare collected per embarkation point (C = Cherbourg, Q = Queenstown, S = Southampton). Then, join this DataFrame with the Titanic dataset on the "Embarked" column.
fare_per_embarkation = titanic_df.groupBy("Embarked").agg({"Fare": "Toal_Sum_Per_Embarkation"})
titanic_df = titanic_df.join(fare_per_embarkation, "Embarked")


# 9. Calculate the survival rate per class and gender.
titanic_df.groupBy(["Sex", "PassengerClass"]).agg({"Survived": "avg"}).show()

    # To print the Survival rate in percentage for each gender in each class
from pyspark.sql.functions import avg, format_number

survival_rates = titanic_df.groupBy(["Sex", "PassengerClass"]).agg(avg("Survived").alias("SurvivalRate"))
survival_rates = survival_rates.select("Sex", "PassengerClass", format_number(survival_rates["SurvivalRate"] * 100, 2).alias("SurvivalRatePercentage"))
survival_rates.show()


# 10. Save the modified DataFrame titanic_df to parquet format and read it back.

titanic_df.write.parquet("titanic.parquet")
newTitanitc_df = spark.read.parquet("titanic.parquet")
newTitanitc_df.show(10)