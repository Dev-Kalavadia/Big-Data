# https://grouplens.org/datasets/movielens/100k/
# MovieLens data sets were collected by the GroupLens Research Project at the University of Minnesota.
 
# This data set consists of:
#	* 100,000 ratings (1-5) from 943 users on 1682 movies. 
#	* Each user has rated at least 20 movies. 
#   * Simple demographic info for the users (age, gender, occupation, zip)

# The main files you'll be working with are:
#	* "u.data" contains the user IDs, movie IDs, ratings, and timestamps. 
#	* "u.item" contains movie titles, and other movie related information

# Load the data from the MovieLense Dataset
raw_rating_data = sc.textFile("data/u.data")

# check if this is an rdd or some other native python datatype
type(raw_rating_data)

# inspect the first 5 elements
raw_rating_data.take(5)

# count the number of ratings
record_count = raw_rating_data.count()

# Extracting unique users and movies
data_split = raw_rating_data.map(lambda line: line.split("\t"))

unique_users = data_split.map(lambda x: int(x[0])).distinct().count()
print(unique_users)

unique_movies = data_split.map(lambda x: int(x[1])).distinct().count()
print(unique_movies)

# Ratings
ratings = data_split.map(lambda x: float(x[2]))
ratings_stats = ratings.stats()

# Filtering high-rated movies
high_rated_movies = data_split.filter(lambda x: float(x[2]) >= 4.0)


# Now we start joining with another information.. the titles
# Loading movie titles from "u.item"
movies_data = sc.textFile("u.item")
movies_split = movies_data.map(lambda line: line.split("|"))

# Mapping movie titles to movie IDs
movie_titles = movies_split.map(lambda x: (int(x[0]), x[1]))

# Joining high-rated movies with movie titles
high_rated_movies_with_titles = high_rated_movies.map(lambda x: (int(x[1]), float(x[2]))).join(movie_titles).map(lambda pair: (pair[0], pair[1][1], pair[1][0]))
high_rated_movies_with_titles.take(5)


# Calculating average rating per movie
movie_ratings = data_split.map(lambda x: (int(x[1]), (float(x[2]), 1)))
movie_ratings_sum_counts = movie_ratings.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
average_ratings_per_movie = movie_ratings_sum_counts.mapValues(lambda sum_count: sum_count[0] / sum_count[1])

# Finding the top-rated movies (Sort)
top_rated_movies = average_ratings_per_movie.join(movie_titles).map(lambda pair: (pair[0], pair[1][1], pair[1][0])).sortBy(lambda x: x[2], ascending=False)
top_rated_movies.take(10)

# Identifying the most active users
user_activity = data_split.map(lambda x: (int(x[0]), 1)).reduceByKey(lambda a, b: a + b).sortBy(lambda x: x[1], ascending=False)
user_activity.take(10)

# Analyzing the distribution of ratings over time
import time
ratings_by_year = data_split.map(lambda x: (time.strftime("%Y", time.localtime(int(x[3]))), 1)).reduceByKey(lambda a, b: a + b).sortByKey()
ratings_by_year.collect()
