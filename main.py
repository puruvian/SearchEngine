import os
from bs4 import BeautifulSoup
from collections import defaultdict
from tokenizer import tokenize
import posting
import shelve
import json
from build_index import buildIndex
from search import create_meta_index, calculate_tfidf, seek_postings, getUrlFromId, loadUrlStorageIntoMemory, cosineScore, getContenders, get_posting_list
from merge import *
from search import *
from nltk.stem import SnowballStemmer
import time



def queryProcessor(query, stemmer: SnowballStemmer, meta_index_dict: dict) -> str:
    '''
    processes the query in various ways, like removing stopwords, so that
    search is more efficient
    '''

    # add more stopwords later
    stopwords = ['a', 'an', 'the', 'and', 'or', 'but', 'of', 'in', 'on', 'at', 'by', 'for', 'as']
    stopwords = [stemmer.stem(word.strip()) for word in stopwords]
    
    # convert to set
    stopwords = set(stopwords)

    

    queryTerms = query.split(' ')

    for i in range(len(queryTerms)):
        queryTerms[i] = queryTerms[i].lower()

    # for each query term, if it's a stopword, remove it
    for term in queryTerms:
        if term in stopwords:
            queryTerms.remove(term)

        if term not in meta_index_dict:
            queryTerms.remove(term)
        


    # join back query with query terms remove
    query = ' '.join(queryTerms)

    return query


if (__name__ == "__main__"):
    

    # # build inverted index, urls
    # indexStorage, urlStorage = buildIndex()
    # devIndexStorage = dict()

    # print # of urls, # of tokens
    # print(len(urlStorage))                  
    

   

    # f = open(index_file)
    # f.seek(meta_index_dict['aaaaa'])
    # print(f.readline())
    # f.close()

    startTime = time.time()

    stemmer = SnowballStemmer(language='english')  
    index_file = 'final_tfidf.txt'
    meta_index_dict = create_meta_index(index_file)     
    searchQuery = input("Enter your search string:\n")     # user's query
    searchQuery = queryProcessor(searchQuery, stemmer, meta_index_dict)   # remove stopwords

    tokens = searchQuery.split(' ')
    tokens = [stemmer.stem(token.strip()) for token in tokens]

    '''
    black car
    black: tf-idf score of 0.6 for document 5
    car: tf-idf score of 0.2 for document 5
    total document 5 tf-idf score is avg(0.6, 0.2) = 0.4
    
    tf = term frequency in document (found in individual posting) / total number of terms in document (found in urlStorage)
    idf = log(total num of documents (found in num of lines of urlStorage) / num of documents with term (length of posting list) + 1) + 1
    tf-idf = tf * idf
    '''
    startTime = time.time()
    # key: docID     value: average tf_idf score
    rankedUrlDict = dict()
    # urlStorage = loadUrlStorageIntoMemory()
    # totalNumberOfDocuments = len(urlStorage)
    # print("Finished getting urlStorage into memory, totalNumberOfDocuments is ", totalNumberOfDocuments)
    f = open(index_file)

    #'black car'
    # tokens is the query tokens
    totalDocs = 45393

    contendersList = getContenders(f, meta_index_dict, tokens)

    if len(tokens) == 1:
        f = open("final_tfidf.txt", 'r')
        ranked_urls = get_posting_list(f, meta_index_dict, tokens[0])
        rankedUrlDict = []
        for posting_tuple in ranked_urls:
            if (len(posting_tuple) == 3):
                rankedUrlDict.append((posting_tuple[0], posting_tuple[2]))
            else:
                print(posting_tuple)
        sorted_ranked_urls = sorted(rankedUrlDict, key=lambda x: x[1], reverse=True)
        top_20_ranked_urls = sorted_ranked_urls[:20]  
    else:
        rankedUrlDict = cosineScore(searchQuery, meta_index_dict, totalDocs, contendersList)
        sorted_ranked_urls = sorted(rankedUrlDict.items(), key=lambda item: item[1], reverse = True)
        top_20_ranked_urls = sorted_ranked_urls[:20]


    
    f.close()

    
# sort rankedUrlList by tf_idf and return the top 5


print("Top 20 ranked urls for the query:")
for doc_id, score in top_20_ranked_urls:
    print(f"Document ID: {doc_id}, Score: {score}")
    print("URL: " + getUrlFromId(doc_id))

endTime = time.time()
elapsedTime = endTime - startTime
print(f"========= Elapsed search time: {elapsedTime:.6f} seconds  =========")
    




    
















