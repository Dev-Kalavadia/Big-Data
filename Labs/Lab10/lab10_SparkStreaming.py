# Create a synthetic stream:
# awk '{print $0; system("sleep .01");}' * | nc -lk 9999

from pyspark.streaming import StreamingContext

sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 1)
lines = ssc.socketTextStream("localhost", 9999)
words = lines.flatMap(lambda line: line.split(" "))
pairs = words.map(lambda word: (word, 1))
wordCounts = pairs.reduceByKey(lambda x, y: x + y)
WSorted = wordCounts.map(lambda x:(x[1],x[0])).transform(lambda x:x.sortByKey(False))
WSorted.pprint()
ssc.start()             # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
