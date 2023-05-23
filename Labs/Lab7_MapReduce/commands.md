# Run WordCount on text input
# Expect to compute the number of words in a dataset.

python3 WordCount.py wheels.txt
python3 WordCount.py -c mrjob.conf -r emr --cluster-id j-2A5H6M0MFUB0E s3://mrjob-446279f938379ca7/data/

# Run MRWordFreqCount on text input
# Computes the frequency of each word
python3 MRWordFreqCount.py wheels.txt
python3 MRWordFreqCount.py -c mrjob.conf -r emr --cluster-id j-2A5H6M0MFUB0E wheels.txt

# find temperature average by city
python3 TempAVG.py temperature.csv

# Sort
python SortData.py int.txt
python3 SortData.py -c mrjob.conf -r emr --cluster-id j-2A5H6M0MFUB0E --jobconf mapred.reduce.tasks=1 int.txt

# Find the most used word (max)
python3 MRMostUsedWord.py wheels.txt