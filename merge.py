import os

'''
Merge Algorithm:

- Combine Two Files at a time

- if two tokens are equal, merge their postings and then output to merged text file
- if one token is less than the other token, output it to the merged text file and then
    increment to next token

    
- have two file pointers
    - one to the start of dev1.txt one to dev2.txt
- if the term that you're currently reading appears alphabetically before the term you're currently reading in dev2,
  you know that the word in dev1 must not exist in dev2, so you can add it into the new file 

'''


def constructFileList(folder_path) -> list["files"]:
    '''
    Returns list of all the files in indices

    '''
    listOfFiles = []
    # List all entries in the directory
    for entry in os.listdir(folder_path):
        # Construct the full path
        entry_path = os.path.join(folder_path, entry)
        # Check if it is a file
        if os.path.isfile(entry_path):
           listOfFiles.append(entry_path)

    return listOfFiles


def mergeAllFiles(folder):
    listOfFiles = sorted(constructFileList(folder))  # Ensure files are sorted for consistent merging
    if not listOfFiles:
        return

    # Initial setup with the first file as base
    currentBaseFile = listOfFiles[0]
    for i in range(1, len(listOfFiles)):
        with open(currentBaseFile, 'r') as baseFile, \
             open(listOfFiles[i], 'r') as mergeFile, \
             open(f"merged{i}.txt", 'w') as outputFile:

            mergeTokens(baseFile, mergeFile, outputFile)

        # Update the base file to the newly merged file
        currentBaseFile = f"merged{i}.txt"
    os.rename(currentBaseFile, 'final_merged.txt')  # Optionally rename the last merged file
           



def openFiles(file1: str, file2: str, mergeNumber: int):
    
    return ( open(file1, 'r'), open(file2, "r"), open(f"merged{mergeNumber}.txt", 'w'))


def mergePostings(postingLine1: str, postingLine2: str) -> str:
    '''
    Merges postings of two equivalent tokens and returns
    '''

    # get part of string that's only the postings
    # parameters are initially formatted like: 'what : (1, 2) (2, 5) (6, 1) (10, 2) (20, 9)'
    postingsListString1 = postingLine1.split(':')[1] 
    postingsListString2 = postingLine2.split(':')[1]

    postingsListString1 = postingsListString1[:-1]
    
    # return concatenated string
    return postingsListString1 + postingsListString2


def mergeTokens(file1: 'fileObj', file2: 'fileObj', writeFile: 'fileObj') -> None:
    '''
    This function merges two files and outputs a new file which contains the merged lists. 
    This calls mergePostings if it finds a term that appears in both. 
    '''
 
    # get the line from the file
    line1 = file1.readline()
    line2 = file2.readline()
    token1 = getTokenFromStr(line1)
    token2 = getTokenFromStr(line2)
    '''
    token1 is less -> read next token1 line
    '''
    inc1 = True

    while (line1 != '' and line2 != ''):
        if token1 == token2:
            postingsList = mergePostings(line1, line2)
            writeToFile(writeFile, f"{token1} : {postingsList}")

            line1 = file1.readline()
            line2 = file2.readline()

        else:
            if token1 < token2:
                writeToFile(writeFile, line1)  # store the current entry
                line1 = file1.readline()  # go to the next entry
            elif token1 > token2:
                writeToFile(writeFile, line2)  
                line2 = file2.readline()  
            
            
        token1 = getTokenFromStr(line1)
        token2 = getTokenFromStr(line2)

    if line1 != "":
        while(line1 != ""):
            writeToFile(writeFile, line1) 
            line1 = file1.readline()
    elif line2 != "":
        while(line2 != ""):
            writeToFile(writeFile, line2)  # store the current entry
            line2 = file2.readline()  # go to the next entry
    
    return None



def getTokenFromStr(line: str) -> str:
    '''
    Gets the token value from the string
    '''
    index = line.find(":")
    return line[:index - 1]



def writeToFile(writeFile: 'fileObj', line: str) -> None:
    writeFile.write(line)


