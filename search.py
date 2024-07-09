import math
import ast  
from functools import reduce


from posting import Posting, ListOfPostings


index_file = 'final_merged.txt'

def parse_index_file(index_file):
    '''
    Reads the file into postings object
    '''
    index = {}
    doc_counts = {}
    total_docs = 0
    with open(index_file, 'r') as file:
        for line in file:
            term, postings = line.split(':')
            # Safer alternative to eval
            postings_list = ast.literal_eval(postings.strip())
            if term not in index:
                index[term] = ListOfPostings()
            for doc_id, freq in postings_list:
                index[term].addPosting(Posting(doc_id, freq))
                if doc_id not in doc_counts:
                    doc_counts[doc_id] = 0
                doc_counts[doc_id] += freq
                total_docs = max(total_docs, doc_id)

    return index, doc_counts, total_docs + 1
'''
-number of times term appears in document
    - this is in final_merged.txt, in each posting (31535, 4)

-total number of terms in document
    -open urlStorage and get number of terms

-total number of documents
    -number of lines in urlStorage.txt

-Number of documents that contain the word
    -number of postings in line in final_merged.txt
    aaaaaa :  (20124,1)  (38673,1) 
'''



# def calculate_tfidf(index, doc_counts, total_docs):
#     tfidf_index = {}
#     for term, postings in index.items():
#         postings_list = postings.getPostings()
#         df = len(postings_list)
#         idf = math.log(total_docs / df) if df else 0
#         for posting in postings_list:
#             doc_id = posting.docID
#             tf = posting.token_freq / doc_counts[doc_id]
#             tfidf = tf * idf
#             if term not in tfidf_index:
#                 tfidf_index[term] = []
#             tfidf_index[term].append((doc_id, tfidf))
#     return tfidf_index

'''
black car
black: tf-idf score of 0.6 for document 5
car: tf-idf score of 0.2 for document 5
total document 5 tf-idf score is avg(0.6, 0.2) = 0.4

tf = term frequency in document (found in individual posting) / total number of terms in document (found in urlStorage)
idf = log(total num of documents (found in num of lines of urlStorage) / num of documents with term (length of posting list) + 1) + 1
tf-idf = tf * idf
'''

def calculate_tfidf(token: str, docID: int, frequency: int, numberOfDocsContainingToken: int, numberOfTermsInDocument: int, totalNumberOfDocuments: int):

    tf  =  (1 + math.log(frequency)) / numberOfTermsInDocument ** 2
    
    #log(total num of documnets / num of documents containing the token)
    idf = math.log((1 + totalNumberOfDocuments)/(numberOfDocsContainingToken + 1))
    
    return tf * idf


    # calculate and return tf_idf



def calculate_query_tf(query_tokens) -> dict:
    '''
    Gets tf_idf weight of each term in query
    
    '''
    termWeights = dict()
    termFrequencies = dict()
    for term in query_tokens:
        if term not in termFrequencies:
            termFrequencies[term] = 1
        else:
            termFrequencies[term] += 1
            
    return termFrequencies


def cosineScore(query, meta_index_dict, total_docs, contendersList) -> dict:
    '''
    Generates the cosine score for each doc, returning a dict with key => docID
    and value => cosine score
    '''
    
    '''
    [1, 2, 3, 4, 5, 6, 7]

    master: 1, 2, 3, 4, 5
    software: 
    engineering
    
    '''

    contendersList = set(contendersList)

    scores = {}     # cosin scores for each document
    lengths = {}     

    query_tokens = query.split() #tokenizes query

    term_frequencies = calculate_query_tf(query_tokens)  # Calculate frequency of each term i in query

    
    
    with open("final_tfidf.txt", 'r') as f:
    # we need to calculate tfidf (which is the weight) for each term in the query
        
        for term in term_frequencies:            
            
            postings_list = get_posting_list(f, meta_index_dict, term)
            if postings_list:
                df = len(postings_list)
                idf = math.log((total_docs + 1) / (df + 1))
                weight_qt = (1 + math.log(term_frequencies[term])) * idf

                
                
                # posting: (docID, freq, tf-idf)
                for posting in postings_list:
                    doc_id, frequency, tf_idf_score = posting
                    
                    if doc_id not in scores:
                        scores[doc_id] = 0
                        lengths[doc_id] = 0

                    scores[doc_id] += tf_idf_score * weight_qt
                    lengths[doc_id] += (tf_idf_score * weight_qt) ** 2

            # we normalize the score
            for doc_id in scores:
                if lengths[doc_id] == 0:
                    print(f"Length is 0, skipping normalization")
                    scores[doc_id] = 0
                else:
                    scores[doc_id] /= math.sqrt(lengths[doc_id])
                    #if doc_id in contendersList:
                    #    scores[doc_id] += 100000   # weight added

    for key in scores:
        if (scores[key] == 0):
            continue
        scores[key] = math.log(scores[key])
        if key in contendersList:
            scores[key] += 3
            pass

    # sort by score descending
    return scores


def getContenders(f: 'FileObject', meta_index, query_terms: list) -> list[int]:
    '''
    Gets 1000 contenders from the documents
    
    If query has 3 terms, then this
        - first gets documents with 3 query terms
        - then gets documents with 2 query terms
        etc. etc.

        until we have 1000

    @return A list of docID's to check with cosine
    '''
    
    # list of docIDs that we will return as our contenders
    contenderList = set()

    
    # dictionary:  key => term    value   =>  list of document ids that contain word
    from collections import defaultdict
    
    dictStorage = defaultdict(set)

    
    # get postings list of each query term
    for term in query_terms:
        if term in meta_index:
            
            # gets string representation of postings
            currentPostingList = get_posting_list(f, meta_index, term)

            # for every posting, add it's docID to dictStorage
            for posting in currentPostingList:
                dictStorage[term].add(int(posting[0]))
          
            #same thing if u wanna use
            #currentPostingList = get_posting_list(f,meta_index,term)
            #for doc_id, _, _ in currentPostingList:
            #    dictStorage[term].add(doc_id) 

    # DictStorage after the above for loop:
    # master: 1, 2, 4, 5, 6, etc. etc.
    # software: 1, 2, 3, 4, 5 etc. etc.
    # engineering: 1, 4, 5, 6, 7 etc. etc.
    
    currentTermLength = len(query_terms)  # master software engineering = 3

    while len(contenderList) < 500 and currentTermLength > 0:   
    # how can we merge them to get all docs?
    # let's use functools.reduce
        terms = chooseTermGroupings(query_terms, currentTermLength)
        
  
        
        currentDict = dict()
        for term_tuples in terms:
            for term in term_tuples:
                currentDict[term] = dictStorage[term]
                        
                # calls intersection on cascading values
            
            common_elements = list(reduce(set.intersection, currentDict.values())) 
            contenderList.update(common_elements)       # adds every element of common_elements to contenderList
            common_elements = []  # clear common_elements after one tuple processed
        
        # clear current dict
        currentDict.clear()
        currentTermLength -= 1


    # do we return a list of document ids?
    return list(contenderList)


def chooseTermGroupings(query_terms:list , num_groupings: int) -> list[tuple]:
    '''
    This function gets the groupings of terms. For example, if query_terms is 
    "master software engineering", and num_groupings is 2, this returns:
    [("master", "software"), ("software", "engineering")]

    If num_groupings is 1, returns:
    [('master',), ('of',), ('software',), ('engineering',)]
    '''
    to_return = []
    startInd = 0
    endInd = num_groupings
    while endInd != len(query_terms) + 1:
        to_return.append(tuple(query_terms[startInd: endInd]))
        startInd += 1
        endInd += 1
    return to_return
    

def get_posting_list(f: "FileObject", meta_index: dict, term: str) -> list[tuple]:
    '''
    Returns a list of all the postings for a particular term in list format
    '''
    if term in meta_index:
        f.seek(meta_index[term])
        line = f.readline()
        split_str = line[line.find(":") + 2:].strip()
        postings = split_str.split(' ')
        to_return = []

        for posting in postings:
            if posting:
                parts = posting.strip("()").split(",")
                doc_id = int(parts[0])
                frequency = int(parts[1])
                tf_idf_score = float(parts[2])
                to_return.append((doc_id, frequency, tf_idf_score))
                
        return to_return
    
    return []
    
def create_meta_index(index_file):
    '''
    Creates 'index of index' for each token in a dictionary
    so we can use file.seek() and jump around the main index
    file efficiently

    THIS TAKES 600 - 650 MS TO RUN
    '''
    meta_index = {}
    with open(index_file, 'r') as file:
        line = file.readline()
        offset = 0
        while line:
            term = line[ :line.find(":")].strip()
            # term = line.partition(":")[0].strip()
            # term = line.split(':')[0].strip()  # changed this line
            meta_index[term] = offset
            offset = file.tell()
            line = file.readline()
    return meta_index

def seek_postings(term, meta_index, index_file):
    if term in meta_index:
        with open(index_file, 'r') as file:
            file.seek(meta_index[term])
            postings_line = file.readline()
            return postings_line.split(':')[1].strip()  
    return None


def getUrlFromId(docId: int):
    with open("urlStorage.txt", "r") as f:
        line = f.readline()
        words = line.strip().split()
        id = words[0]
        while (int(id) != docId):
            line = f.readline()
            words = line.strip().split()
            id = words[0]
        return words[2]
    

def loadUrlStorageIntoMemory() -> "dict(int : tuple(url, fileName, termCount))":
    '''''''''
    Load doc ids and they urls they represent into memory at beginning of program
    by putting them in a dictionary
    '''
    
    urlStorageDict = dict()
    with open("urlStorage.txt", "r") as f:
        for line in f:
            
            partsOfLine = line.split(' ')

            docID = int(partsOfLine[0])

            url = partsOfLine[2]  # after colon
            fileName = partsOfLine[3]
            termCount = int(partsOfLine[4])

            urlStorageDict[docID] = (url, fileName, termCount)

    return urlStorageDict


