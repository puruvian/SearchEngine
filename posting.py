
# class to represent indivdual posting
# for now only has docID and frequency but can add fields, etc. later
class Posting:
    def __init__(self, id: int, freq: int) -> None:
        self.docID = id
        self.token_freq = freq


# class to represent list of postings
# decided to use a class in order to make potential future changes slightly easier
class ListOfPostings:
    def __init__(self) -> None:
        self.postingsList = list()

    def addPosting(self, posting) -> None:
        '''
        add posting to posting list

        '''

        self.postingsList.append(posting)

    def getLength(self) -> int:
        '''
        return length
        '''

        return len(self.postingsList)
    
    def getStringOfPostings(self) -> None:
        '''
        return string representation of list of postings so it's easier to write to file
        '''
        postingsListString = ''

        for posting in self.postingsList:
            singlePostingString = '(' + str(posting.docID) + ',' + str(posting.token_freq) + ') '
            postingsListString += singlePostingString

        return postingsListString
    




            
