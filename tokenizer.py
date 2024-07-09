from collections import defaultdict

# Runtime Complexity: O(N) where n is # of characters in file
# since as n grows, the amount of time our program will take in
# the worst-case will grow linearly, as we are iterating through
# each character in the file one time
def tokenize(inputString):
    '''
    returns a list of all alphanumeric words in the inputted text file
    '''

    result = []
    currentWord = ""

    i = 0
    while i < len(inputString):
        char = inputString[i]             # get character from file

        if not char:            # if character doesn't exist, break loop
            break

        if char.isalnum() and ord(char) <= 127 or char == "'":
            # if current character is alphanumeric, then add
            currentWord += char.lower()

        # if current character is not alphanumeric, reset
        else:
            if currentWord != "":
                result.append(currentWord)
            currentWord = ""

        i += 1

    # add last word if it exists
    if currentWord != "":
        result.append(currentWord)

    return result


# Runtime Complexity: O(N), where n is the number of values in
# the argument tokenList; This is because we are iterating through
# each item in tokenList one time, so as n grows, the runtime of our
# program will grow linearly
def computeWordFrequencies(tokenList):
    '''
    Returns a dictionary containing the frequency of each word
    in tokenList
    '''

    result = dict()

    # for every token in list, increment its frequency
    for token in tokenList:
        #if token already exists in dictionary, increment it's value
        if token in result:
            result[token] += 1

        # if token doesn't exist as key in dictionary, initialize it's value to 1
        else:
            result[token] = 1

    return result
