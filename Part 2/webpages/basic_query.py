import json
import string
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import math

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from collections import defaultdict
from num2words import num2words

class basicQuery:

    def __init__(self, query: str):
        """create a query object that will search in json files for the item and return 

        Args:
            query (str): [the word that you are searching]
        """
        #lower and lemmatize query
        self.originalQuery = query
        self.query = self.queryPrep(query)
        self.documentCount = self.getDocumentCount()

        with open("data\\bookkeeping.json", 'r', encoding = "utf-8") as infile:
            self.bookkeeping = json.load(infile)

    def queryPrep(self, query:str):
        query = query.lower()
        lemmatizer = WordNetLemmatizer()
        query = lemmatizer.lemmatize(query)
        new_query = ""
        for term in query.split():
            try:
                term = num2words(term, lang="en")
                new_query += term
            except:
                new_query += term
                pass
            new_query += " "
        return new_query

    def getDocumentCount(self):
        with open("data\\documentCount.txt", 'r', encoding = "utf-8") as infile:
            return int(infile.read())


    def getResults(self, numberOfWebsites: int):
        """This function returns the top numberOfWebsites from the query

        Args:
            numberOfWebsites (int): the number of websites to return
        """

        termList = self.query.split()
        
        #query
        queryWtList = []

        for term in set(termList):
            #calc weighted tf
            tf = termList.count(term)
            tfWeighted = 1 + math.log( tf,10)
            
            #get df
            df = len(self.retrieveListOfFiles(term))
            idf = math.log(self.documentCount/df)

            wt = tfWeighted * idf
            queryWtList.append(wt)

        queryLength = 0
        for num in queryWtList:
            queryLength += num ** 2
        queryLength = queryLength ** 0.5

        normalizedQueryList = [x/queryLength for x in queryWtList]


        #documents
        docSet = set()
        for term in set(termList):
            docsToCrawlThrough = self.retrieveListOfFiles(term)
            for doc in docsToCrawlThrough:
                docSet.add(doc[1])
        
        #form: documentDict["0/0"]["word"] = wt#
        documentDict = {}
        for doc in docSet:
            documentDict[doc] = defaultdict(float)
            for term in set(termList):
                docsToCrawlThrough = self.retrieveListOfFiles(term)
                for innerDoc in docsToCrawlThrough:
                    if innerDoc[1] == doc:
                        documentDict[doc][term] = innerDoc[0]
        
        scoreDict = {}

        for doc in documentDict.keys():
            docLength = 0
            documentWtList = []
            for term in termList:
                docLength += (documentDict[doc][term] ** 2)
                documentWtList.append(documentDict[doc][term])
            docLength = docLength ** 0.5
            normalizedDocumentList = [x/docLength for x in documentWtList]
            score = 0
            for i in range(len(termList)):
                score += (normalizedDocumentList[i] * normalizedQueryList[i])
            scoreDict[doc] = score
        
        #highest scores at the front
        sortedKeys = sorted(scoreDict, key = scoreDict.__getitem__, reverse = True)
        urlList = self.getUrls(sortedKeys)
        if int(numberOfWebsites) > len(urlList):
            numberOfWebsites = len(urlList)
        for i in range(int(numberOfWebsites)):
            print(urlList[i])

    def retrieveListOfFiles(self, term):
        """returns a list of lists that contain file structure of form: [[wt #, file #s], [3.22412, "0/0"]]

        Returns:
            [list of str]: [returns a list of strings]
        """
        firstChar = term[0]
        if firstChar not in string.ascii_lowercase:
            firstChar = "mischellenous"

        with open("data\\"+firstChar+".json", "r", encoding = "utf-8") as infile:
            firstCharDict = json.load(infile)
            if term in firstCharDict.keys():
                return firstCharDict[term]
            else:
                print(f"Term: {term} not in the index")


    def getUrls(self, listOfFiles):
        """takes a list of files of from ["0/0", "1/12",...]returns a list of urls in str form. 

        Args:
            listOfFiles ([list of str]): [list of urls in str]
        """
        listOfUrls = []
        for file in listOfFiles:
            listOfUrls.append(self.bookkeeping[file])
        return listOfUrls

 

if __name__ == "__main__":
    myQuery = basicQuery("computer science")
    myQuery.getResults(20)
        
        
