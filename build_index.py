from tokenizer import tokenize
from tokenizer import computeWordFrequencies
from bs4 import BeautifulSoup
import os
from bs4 import BeautifulSoup
from collections import defaultdict
from tokenizer import *
import posting
import shelve
import json
from posting import Posting
from posting import ListOfPostings
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import search
import merge




def buildIndex() -> None:
    '''
    iterate through every file and build out an inverse index represented
    through a dictionary

    @return: 
    '''

    # dictionary with key of token and value of list of postings
    indexStorage = dict()

    # dictionary that stores which url each docID represents
    # key: doc ID  =>   value: (url, filename, number of terms in document)
    urlStorage = dict()

    # currentDocID (will get incremented as we iterate through each file)
    docID = 1

    # used to count number of documents so we can load off files to disk periodically
    docCount = 0

    # file count is used for naming new files
    fileCount = 1

    for root, dirs, files in os.walk("./DEV"):
        for file in files:
            fileToOpen = os.path.join(root, file)       # get actual path of file

            with open(fileToOpen, "r", errors='ignore') as current_file:
                try:
                    data = json.loads(current_file.read())
                    #posting.process_file(data["content"], indexStorage)
                    html_content = data["content"]

                    # Extract all text elements from the parsed HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    text = soup.get_text()

                    # tokenize html, get list of all tokens
                    #tokens = tokenize(text)
                    #tokens =  word_tokenize(text)
                    tokenizer = RegexpTokenizer(r'\b[a-zA-Z]+\b')
                    tokens = tokenizer.tokenize(text)

                    # Use porter stemmer to standardize all words
                    # ex: turns [likely, liking] => [like, like]
                    stemmer = SnowballStemmer(language='english')
                    stemmed_tokens = [stemmer.stem(token) for token in tokens]


                    # get dictionary that has counts of all tokens
                    tokenFrequencies = computeWordFrequencies(stemmed_tokens)

                    # iterate through tokens
                    for token in tokenFrequencies.keys():
                        # if token not in indexStorage then add it as a key with value being empty ListOfPostings
                        if token not in indexStorage:
                            indexStorage[token] = ListOfPostings()

                        # Create new posting object with specified id and frequency
                        currentPosting = Posting(docID, tokenFrequencies[token])      

                        # append new Posting object to indexStorage[token]
                        indexStorage[token].addPosting(currentPosting)

                    # set docID to point to new url 
                    urlStorage[docID] = (data['url'], file, len(stemmed_tokens))         # file is the name of the file, url is the url
                    
                    # increment docID
                    docID += 1
                    docCount += 1

                    # if number of documents has reached threshold, output to disk, clear dictionary, and reset docCount
                    if docCount >= 10000:
                        outputToFile(indexStorage, fileCount)
                        indexStorage = dict()
                        docCount = 0
                        fileCount += 1

                    # print(f"finished parsing document, doc count is {docCount}")
                except json.decoder.JSONDecodeError as e:
                    continue

    outputToFile(indexStorage, fileCount)
    outputUrlStorageToFile(urlStorage)
    docCount = 0
    fileCount += 1

    return indexStorage, urlStorage


def outputToFile(indexStorage, fileCount: int) -> None:
    '''
    loads off files from indexStorage in order to meet constraint
    '''
    with open(f'indices/dev_index{fileCount}.txt', 'w') as file:
        indexStorage = dict(sorted(indexStorage.items()))  # sorts by key, which is the term
        for key in indexStorage:
            file.write(key + " : "  + indexStorage[key].getStringOfPostings() + '\n')
    print(f"Wrote to file with file count: {fileCount}")
    # clear dictionary to free up memory
    indexStorage.clear()

def outputUrlStorageToFile(urlStorage):
    with open(f'urlStorage.txt', 'w') as file:
        for key in urlStorage:
            file.write(str(key) + " : "  + str(urlStorage[key][0]) + ' ' + str(urlStorage[key][1]) + ' ' + str(urlStorage[key][2]) + '\n')

    
def build_tf_idf_index():
    '''
    This function takes the final_merged.txt file and copies it to a new file called final_tfidf.txt, 
    which includes the tf_idf of each posting. 
    '''
    totalNumberOfDocuments = 45393  # constant
    urlStorage = search.loadUrlStorageIntoMemory()
    with open('final_merged.txt', 'r') as f:
        f_write = open("final_tfidf.txt", 'w')
        line = f.readline()

        while (line != ""):
            term = line[ :(line.find(":") - 1)]
            line = line[line.find('('):].strip()
            line_split = line.split(" ")
            to_write = [f"{term} :"]

            for posting in line_split:
                split = posting[1:-1].split(",")  # parts of the tuple are the first and second number
                if split == [""]:
                    continue
                docID = int(split[0])
                frequency = int(split[1])
                tf_idf = search.calculate_tfidf(term, docID, frequency, len(line_split), int(urlStorage[docID][2]), totalNumberOfDocuments)
                to_write.append(f"({docID},{frequency},{round(tf_idf, 4)})")

            writeTfIdfToFile(to_write, f_write)
            line = f.readline()

        f_write.close()

def writeTfIdfToFile(lines: list, f: 'FileObject'):
    '''
    This function writes a line to the final_tfidf.txt including the new posting list.
    lines is a list of strings to write to the file.
    '''
    line = " ".join(lines)
    f.write(line)
    f.write('\n')

if __name__ == "__main__":
    buildIndex()
    merge.mergeAllFiles("indices")
    build_tf_idf_index()
    