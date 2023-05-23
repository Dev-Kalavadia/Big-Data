# Find the number of distinct names by "first letter"
mylist = sc.parallelize(['alba', 'david', 'boyl', 'doris', 'bob', 'brave'])
mylist_map = mylist.map(lambda name: (name[0], name))
cvalues = mylist_map.groupByKey()
counts = cvalues.mapValues(lambda name: len(set(name)))
counts.collect()


# word frequency count (note: you can read from a directory, but you'll loose the file name)
text_file = sc.textFile('datain/wheels.txt')
counts = text_file.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
counts.collect()

# total word count per file (notice that we are reading from a directory here)
files = sc.wholeTextFiles("./datain")
files.map(lambda x: (x[0], x[1].split())).mapValues(lambda x: len(set(x))).collect()

# Estimating pi
import random
NUM_SAMPLES = 10000
def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1
count = sc.parallelize(range(0, NUM_SAMPLES)).filter(inside).count()
print(count*4.0/NUM_SAMPLES)