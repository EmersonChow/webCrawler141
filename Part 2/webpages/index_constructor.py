#names
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import os
import string
import re
import lxml
from _collections import defaultdict
from num2words import num2words
import math

class Index_Constructor:

    def __init__(self):
        self.index = defaultdict(list)
        self.DFDict = {}
        self.counterDict = {}
        self.totalDocNum = 0
        with open("data\\bookkeeping.json", 'r', encoding = "utf-8") as infile:
            self.bookkeeping = json.load(infile)

    def getNumDoc(self):
        return self.totalDocNum

    def getNumUnqiueWords(self):
        return len(self.index.keys())

    def getHTMLFile(self, folder:str, fileNum: str):
        relativePath = os.getcwd()
        newPath = f"{relativePath}\\WEBPAGES_RAW\\{folder}\\{fileNum}"
        return newPath

    def counter(self):
        """returns a dict with words to len(doc)"""
        counterDict = {}
        for key in self.DFDict.keys():
            counterDict[key] = len(self.DFDict[key])
        self.counterDict = counterDict

    def getTfIDF(self, tfNum, term):
        """returns tfidf """
        #return tfNum * math.log(self.totalDocNum/(self.counterDict[term]), 10)
        weightedTfIDF = (1+math.log(tfNum,10))
        if weightedTfIDF >0:
            return weightedTfIDF
        else:
            return 0

    def createDFDict(self):
        for key, value in self.bookkeeping.items():
            split_keys = key.split("/")
            folder = split_keys[0]
            fileNum = split_keys[1]
            filePath = self.getHTMLFile(folder, fileNum)
            with open(filePath, 'r', encoding = "utf-8") as htmlFile:
                html = htmlFile.read()
                
                if re.search("<HTML>", html) != None:
                    #create DFDict
                    throwaway = self.extractTokens(html, key, True)

    def insertIntoIndex(self):
        self.createDFDict()
        for key, value in self.bookkeeping.items():
            split_keys = key.split("/")
            folder = split_keys[0]
            fileNum = split_keys[1]
            filePath = self.getHTMLFile(folder, fileNum)
            with open(filePath, 'r', encoding = "utf-8") as htmlFile:
                html = htmlFile.read()
                
                if re.search("<HTML>", html) != None:
                    self.totalDocNum += 1
                    #create DFDict
                    tokenDictList = self.extractTokens(html, key, False)
                    #create counterDict
                    self.counter()

                    termSet = set()
                    #get all unique word set
                    for dictionary in tokenDictList:
                        for term in dictionary.keys():
                            termSet.add(term)
                    #iterate through every word through every dictionary to get tfidf numbers
                    p_weight = 1.1
                    h_weight = 1.25
                    em_weight = 1.15
                    bold_weight = 1.15
                    title_weight = 1.35

                    for term in termSet:
                        tfidf = 0
                        #p_dict
                        if term in tokenDictList[0]:
                            tfidf += self.getTfIDF(tokenDictList[0][term][1], term) * p_weight
                        if term in tokenDictList[1]:
                            tfidf += self.getTfIDF(tokenDictList[1][term][1], term) * h_weight
                        if term in tokenDictList[2]:
                            tfidf += self.getTfIDF(tokenDictList[2][term][1], term) * em_weight
                        if term in tokenDictList[3]:
                            tfidf += self.getTfIDF(tokenDictList[3][term][1], term) * bold_weight
                        if term in tokenDictList[4]:
                            tfidf += self.getTfIDF(tokenDictList[4][term][1], term) * title_weight
                        self.index[term].append((tfidf, key))
                                                # (3.23142, "0/0")
                    



                    

    
    def extractTokensHelper(self, soupList, documentWordCount, key, createDFDict):
        """
            takes a list of beautifulSoup element Tag objects and returns a list of tokens
            Does some preprocessing steps: lemmatization, stopword removal, num2words
        """    
        
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))

        p_dict = defaultdict(int)    
        for soupObject in soupList:
            text_tokens = nltk.tokenize.word_tokenize(soupObject.text)
            for textToken in text_tokens:
                if (textToken not in string.punctuation) and (textToken not in stop_words):
                    #lemmatize
                    new_wrd = lemmatizer.lemmatize(textToken)
                    new_wrd = new_wrd.lower()

                    #change numbers to words if they're in decimals
                    try:
                        new_wrd = num2words(new_wrd, lang="en")
                    except:
                        pass
                    
                    if createDFDict:

                        try:
                            self.DFDict[new_wrd].add(key)
                        except:
                            self.DFDict[new_wrd] = {key}

                    p_dict[new_wrd] += 1
                    documentWordCount += 1
        return p_dict,documentWordCount

 

    # include lemmatization at this step
    def extractTokens(self, html: str, key: str, createDFDict: bool):
        """if createDFDict is True, we will create our DFDict"""
        soup = BeautifulSoup(html, "lxml")
        documentWordCount = 0
        #p
        allP = soup.find_all('p')
        p_dict_tuple = self.extractTokensHelper(allP, documentWordCount, key, createDFDict)
        p_dict = p_dict_tuple[0]
        documentWordCount = p_dict_tuple[1]

        #headers
        allH = soup.find_all(re.compile("^h[1-6]"))
        h_dict_tuple = self.extractTokensHelper(allH, documentWordCount, key, createDFDict)
        h_dict = h_dict_tuple[0]
        documentWordCount = h_dict_tuple[1]
        
        #emphasis
        allEm = soup.find_all('em')
        em_dict_tuple = self.extractTokensHelper(allEm, documentWordCount, key, createDFDict)
        em_dict = em_dict_tuple[0]
        documentWordCount = em_dict_tuple[1]

        #bold
        allBold = soup.find_all('b')
        bold_dict_tuple = self.extractTokensHelper(allBold, documentWordCount, key, createDFDict)
        bold_dict = bold_dict_tuple[0]
        documentWordCount = bold_dict_tuple[1]

        #title
        allTitle = soup.find_all('title')
        title_dict_tuple = self.extractTokensHelper(allTitle, documentWordCount, key, createDFDict)
        title_dict = title_dict_tuple[0]
        documentWordCount = title_dict_tuple[1]
        #this is just raw counts, using bag of words model -> uses raw counts
        documentWordCount = 1
        
        p_dict_freq = defaultdict(tuple)
        for key, value in p_dict.items():
            p_dict_freq[key] = (value, value/documentWordCount)

        h_dict_freq = defaultdict(tuple)
        for key, value in h_dict.items():
            h_dict_freq[key] = (value, value/documentWordCount)
        
        em_dict_freq = defaultdict(tuple)
        for key, value in em_dict.items():
            em_dict_freq[key] = (value, value/documentWordCount)

        bold_dict_freq = defaultdict(tuple)
        for key, value in bold_dict.items():
            bold_dict_freq[key] = (value, value/documentWordCount)

        title_dict_freq = defaultdict(tuple)
        for key, value in title_dict.items():
            title_dict_freq[key] = (value, value/documentWordCount)

        dictList = [p_dict_freq,h_dict_freq, em_dict_freq, bold_dict_freq, title_dict_freq]

        return dictList
    
#"a": [(0.15, "0/0")]
    def create_json(self):
        """
            creates the json index file that we will use to store our data
        """
        done = False
        alphabetIndexer = 0
        alphabet = string.ascii_lowercase

        while(not done):
            sortedIndexKeys = sorted(self.index.keys())
            throwAwayDict = {}
            breaker = False
            for key in sortedIndexKeys:
                if breaker:
                    break
                elif(key[0] in alphabet):
                    if(key[0] == alphabet[alphabetIndexer]):
                        throwAwayDict[key] = self.index[key]
                        self.index.pop(key)
                    else:
                        breaker = True
            
            
            if len(throwAwayDict.keys()) > 0:
                textFileName = "data\\" + alphabet[alphabetIndexer] + ".json"
                with open(textFileName, 'w', encoding = "utf-8") as outfile:
                    json.dump(throwAwayDict, outfile)

            alphabetIndexer += 1
            if alphabetIndexer > 26:
                with open("data\\mischellenous.json", 'w', encoding = "utf-8") as outfile:
                    json.dump(self.index, outfile)
                done = True
        with open("data\\documentCount.txt", 'w', encoding = "utf-8") as outfile:
            outfile.write(str(self.totalDocNum))

            
if __name__ == "__main__":
    x = Index_Constructor()
    x.insertIntoIndex()
    x.create_json()


            
    
    
        
            
        

        
