#names
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import os
import string

class Index_Constructor:

    def __init__(self):
        self.index = defaultdict(list)
        self.numDoc = 0
        with open("data\\bookkeeping.json", 'r', encoding = "utf-8") as infile:
            self.bookkeeping = json.load(infile)

    def getNumDoc(self):
        return self.numDoc

    def getNumUnqiueWords(self):
        return len(self.index.keys())

    def getHTMLFile(self, folder:str, fileNum: str):
        relativePath = os.getcwd()
        newPath = f"{relativePath}\\WEBPAGES_RAW\\{folder}\\{fileNum}"
        return newPath

    def insertIntoIndex(self):
        for key, value in self.bookkeeping.items():
            self.numDoc +=1
            split_keys = key.split("/")
            folder = split_keys[0]
            fileNum = split_keys[1]
            filePath = self.getHTMLFile(folder, fileNum)
            with open(filePath, 'r', encoding = "utf-8") as htmlFile:
                html = htmlFile.read()
                tokens = self.extractTokens(html)
                tokenDict = defaultdict(int)
                for token in tokens:
                    tokenDict[token] += 1
                    #this value can be used later for ranking. For now it will only handle duplicates
                for uniqueToken in tokenDict.keys():
                    self.index[uniqueToken].append(key)

    
            
    # include lemmatization at this step
    def extractTokens(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        text_tokens = nltk.tokenize.word_tokenize(soup.get_text())
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        new_text_tokens =[]
        for wrd in text_tokens:
            #maybe look into unicode words because some random things break through like as^tm sign
            if (wrd not in string.punctuation) and (wrd not in stop_words):
                #lemmatize
                new_wrd = lemmatizer.lemmatize(wrd)
                new_wrd = new_wrd.lower()
                new_text_tokens.append(new_wrd)
        
        return new_text_tokens
    
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
            

            


        
            
        

        
