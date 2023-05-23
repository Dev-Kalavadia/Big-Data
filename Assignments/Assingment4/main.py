# Assingment 4: Inverted Index 
# Dev Kalavadiya - dk3936 

from mrjob.job import MRJob
from mrjob.step import MRStep
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import string
import os

# index_mapping = {}
# # get all the file names in the file folder:
# for file in os.listdir("documentsTest"):
#     if file.endswith(".txt"):
#         index_mapping[file] = len(index_mapping)+1
        
# print(index_mapping)

# # write the index_mapping to a file
# with open('index_mapping.txt', 'w') as f:
#     for key, value in index_mapping.items():
#         f.write("%s,%s" % (key, value))
#         f.write("\n")

class MRInvertedIndex(MRJob):
    vocabulary_set = set()
    stemmer = SnowballStemmer('english')
    stopwords = set(stopwords.words('english'))
    def mapper_get_words(self, _, line):
        # Get the current file name
        file_name = os.environ['map_input_file']
        # yield each stemmed word in the line
        for word in word_tokenize(line):
            # Remove punctuation and numbers
            word = word.translate(str.maketrans('', '', string.punctuation + string.digits))
            # Stem the word
            stemmed_word = self.stemmer.stem(word.lower())
            # Filter out stopwords
            if stemmed_word not in self.stopwords:
                yield (stemmed_word, {file_name: 1})
                # Append new words to vocabulary set
                if stemmed_word not in self.vocabulary_set:
                    self.vocabulary_set.add(stemmed_word)

    def reducer_merge_counts(self, word, file_count_dicts):
        file_count = {}
        # Merge counts for each file
        for count_dict in file_count_dicts:
            for file_name, count in count_dict.items():
                if file_name not in file_count:
                    file_count[file_name] = 0
                file_count[file_name] += count
        yield word, file_count

    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_words,
                   reducer=self.reducer_merge_counts)
        ]

if __name__ == '__main__':
    MRInvertedIndex.run()
