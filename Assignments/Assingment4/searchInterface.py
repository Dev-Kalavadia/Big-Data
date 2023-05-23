# Assingment 4: Inverted Index 
# Dev Kalavadiya - dk3936 

from collections import defaultdict
import os
import math
import time
import glob
import json
import string
from colorama import Fore, Style

RESULTS_DIR = 'InvertedIndex'

# Loading stopwords
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))

# Defining a function to load the inverted index from file
def load_inverted_index():
    print("Loading inverted Index from the results")
    inverted_index = defaultdict(list)
    # Looping through each file in the results folder
    for file_path in glob.glob(os.path.join(RESULTS_DIR, '*')):
        with open(file_path, 'r') as f:
            print("loading", file_path)
            for line in f:
                word, doc_freq = line.strip().split('\t')
                word = word[1:-1]
                # print(word)
                doc_freq = json.loads(doc_freq)
                for doc, freq in doc_freq.items():
                    inverted_index[word].append([doc, freq])
                #Sorting the word in inverted_index based on the frequency in descending order
                inverted_index[word] = sorted(inverted_index[word], key=lambda x: x[1], reverse=True)
        # print()
    return inverted_index

#Inital function for searching the inverted index just by the top frequency of the word
# def search_inverted_index(inverted_index, keyword):
#     # Stem the keyword using the SnowballStemmer
#     from nltk.stem import SnowballStemmer
#     stemmer = SnowballStemmer('english')

#     keyword = stemmer.stem(keyword.lower())
#     # Check if the keyword is in the inverted index
#     if keyword in inverted_index:
#         # Sort the documents by their frequency
#         # print("getting the keyword values for" ,keyword ,inverted_index[keyword])
#         results = (inverted_index[keyword])
#         # Return the top-10 results in the list if there are top but if less then return the all the results
#         if len(results) > 10:
#             return results[:10]
#         else:
#             return results
#     else:
#         return []
    
# Function to search the inverted index for a keyword and return the top-10 relevant documents using TFIDF
def search_inverted_index(inverted_index, keyword):
    # Stemmingthe keyword using the SnowballStemmer
    from nltk.stem import SnowballStemmer
    stemmer = SnowballStemmer('english')
    keyword = stemmer.stem(keyword.lower())
    
    # Checking if the keyword is in the inverted index
    if keyword in inverted_index:
        # Sort the documents by their frequency
        # print("getting the keyword values for" ,keyword ,inverted_index[keyword])
        results = inverted_index[keyword]
        results.sort(key=lambda x: x[1], reverse=True)

        # Calculating IDF (inverse document frequency) for the keyword
        N = len(inverted_index)
        df = len(results)
        idf = math.log10(N / df)
        
        # Calculating TFIDF score for each document
        tfidf_results = []
        for result in results:
            doc_id = result[0]
            tf = result[1]
            tfidf = tf * idf
            tfidf_results.append((doc_id, tfidf))
        
        # Returning the top-10 results in the list if there are top but if less then return the all the results
        if len(tfidf_results) >= 10:
            return tfidf_results[:10]
        else:
            return tfidf_results
    else:
        return []

# Function to search the inverted index for multiple keyword and return the top-10 relevant documents using TFIDF
def searchMulti_inverted_index(inverted_index, keywords):
    # Import necessary libraries
    import math
    from nltk.stem import SnowballStemmer
    # Create a dictionary to store the TFIDF scores for each document
    tfidf_scores = {}
    # Loop through each keyword in the input string
    for keyword in keywords.split():
        # Stemming the keyword using the SnowballStemmer
        stemmer = SnowballStemmer('english')
        keyword = stemmer.stem(keyword.lower())
        
        # Checking if the keyword is in the inverted index
        if keyword in inverted_index:
            # Sort the documents by their frequency
            results = inverted_index[keyword]
            results.sort(key=lambda x: x[1], reverse=True)

            # Calculating IDF (inverse document frequency) for the keyword
            N = len(inverted_index)
            df = len(results)
            idf = math.log10(N / df)

            # Calculating TFIDF score for each document
            for result in results:
                doc_id = result[0]
                tf = result[1]
                tfidf = tf * idf
                if doc_id in tfidf_scores:
                    tfidf_scores[doc_id] += tfidf
                else:
                    tfidf_scores[doc_id] = tfidf
    
    # Sorting the documents by their total TFIDF score
    sorted_docs = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Returning the top-10 results in the list if there are top but if less then return all the results
    if len(sorted_docs) >= 10:
        return sorted_docs[:10]
    else:
        return sorted_docs


def find_index(words, keyword):
    for i, word in enumerate(words):
        if keyword in word:
            return i
    return -1

def display_search_results(results, keyword):
    #get current working directory
    from nltk.stem import SnowballStemmer
    stemmer = SnowballStemmer('english')
    keyword = keyword.lower()
    cwd = os.getcwd()
    print("current working directory is", cwd)
    if not results:
        print('No results found')
    else:
        print('Top-10 documents:')
        for i, result in enumerate(results):
            with open((cwd+result[0][6:]), 'r') as f:
                title = f.readline().strip()
                preview_length = 4
                for line in f:
                    line = line.lower()
                    translator = str.maketrans('', '', string.punctuation.replace('-', ''))
                    line = line.translate(translator)
                    # Replacing hyphen with space
                    line = line.replace('-', ' ')
                    if keyword in line:
                        # print(line, words)       # Printing line and words for debugging purposes                                          
                        words = word_tokenize(line)
                        if keyword in words:
                            index = words.index(keyword)
                        else:
                            # Keyword not found in the current line, continue searching in the subsequent lines
                            continue
                        start_index = max(0, index-preview_length) 
                        end_index = min(len(words), index+preview_length+1)
                        preview_words = words[start_index:end_index]
                        for j in range(len(preview_words)):
                            if preview_words[j] == keyword:
                                preview_words[j] = f"{Fore.RED}{Style.BRIGHT}{preview_words[j]}{Style.RESET_ALL}"
                        preview = ' '.join(preview_words)
                        print(f'Doc:{result[0][-11:]} ({result[1]})  (Article:{title[5:]})  #.. {preview}')
                        break # Break 

def displayMulti_search_results(results, keywords):
    keywords = keywords.split()
    #get current working directory
    found_keyword = False
    cwd = os.getcwd()
    print("current working directory is", cwd)
    if not results:
        print('No results found')
    else:
        previews_printed = {} 
        for result in results:
            previews_printed[result[0]] = False
        for keyword in keywords:
            keyword = keyword.lower()
            print(f'Search results for keyword "{keyword}":')
            for result in results:
                with open((cwd+result[0][6:]), 'r') as f:
                    title = f.readline().strip()
                    preview_length = 4
                    found_keyword = False
                    for line in f:
                        line = line.lower()
                        translator = str.maketrans('', '', string.punctuation.replace('-', ''))
                        line = line.translate(translator)
                        line = line.replace('-', ' ')
                        words = word_tokenize(line)
                        if keyword in words:
                            for word in words:
                                if word == keyword:
                                    if not previews_printed[result[0]]:
                                        previews_printed[result[0]] = True
                                        found_keyword = True
                                        index = words.index(keyword)
                                        start_index = max(0, index-preview_length)
                                        end_index = min(len(words), index+preview_length+1)
                                        preview_words = words[start_index:end_index]
                                        for j in range(len(preview_words)):
                                            if preview_words[j] == keyword:
                                                preview_words[j] = f"{Fore.RED}{Style.BRIGHT}{preview_words[j]}{Style.RESET_ALL}"
                                        preview = ' '.join(preview_words)
                                        print(f'Doc:{result[0][-11:]} ({result[1]})  (Article:{title[5:]})  #.. {preview}')
                                    continue
            if found_keyword:
                break

# Load the inverted index
inverted_index = load_inverted_index()

# Fucntion to print the user interface 
def printMenu():
    print("--------------------------------------------")
    print("Welcome to the search Terminal Interface")
    print("--------------------------------------------")
    print("Enter a keyword/Keywords to search for the top relevant document: ")
    print("Enter !quit to exit the search engine")
    print("Enter !debug to print the inverted index")
    print("Enter !menu to print the menu")

while True:
# Defining a prompt for the user to input a keyword
    printMenu() 
    keyword = input('Enter a keyword (or "quit" to exit): ')
    if keyword == '!quit':
        print("Exiting Search terminal Interface")
        break
    if keyword == '!debug':
        print(inverted_index)
        continue
    if keyword == '!menu':
        printMenu()
        continue
    #lowering the keyword/keywords
    keyword = keyword.lower()
    if len(keyword.split()) == 1:
        start_time = time.time()
        results = search_inverted_index(inverted_index, keyword)
        display_search_results(results, keyword)
        elapsed_time = time.time() - start_time
        # Printing the elpased time taken for the search 
        print(f"About {len(results)} in \033[31m({elapsed_time:.2f} seconds)\033[0m")
    else:
        start_time = time.time()
        results = searchMulti_inverted_index(inverted_index, keyword)
        # print("results", results)         #For debugging purposes
        displayMulti_search_results(results, keyword)
        elapsed_time = time.time() - start_time
        # Printing the elpased time taken for the search 
        print(f"About {len(results)} in \033[31m({elapsed_time:.2f} seconds)\033[0m")
    print() 



