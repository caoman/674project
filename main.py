'''
Created on Sep 4, 2013

@author: lilong
'''
import nltk, string, os
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import PorterStemmer
from sets import Set
from bs4 import BeautifulSoup

docCardinality = 0  #record the number of doc files in total
docList = []
tokenList = Set()

class Doc:
    sentences = []
    
    def __init__(self, topic, title, text):
        self.topic = topic
        self.title = title
        self.text = text

    #get the tokens for all sentences, remove stop words, punctuation, stemming and lemmatization 
    def getAllTokens(self):
        #nltk.download()
        sents = sent_tokenize(self.text)
        tokens = [token for sent in sents for token in word_tokenize(sent) if token not in stopwords.words('english') and string.punctuation.find(token) == -1]
        porter = PorterStemmer()
        lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
        tokens = map(lambda token: lmtzr.lemmatize(porter.stem(token)), tokens)
        return tokens
    
    def getFreqVec(self):
        tokens = self.getAllTokens()
        freqVec = {}
        for token in tokens:
            if freqVec.has_key(token):
                freqVec[token] += 1
            else:
                freqVec[token] = 0
        return freqVec
    
    def outputFreqVec(self):
        freqVec = self.getFreqVec()
        vecStr  = self.topic + "\n{" + ",".join([key + ":" + str(val) for key, val in freqVec.iteritems()]) + "}\n" 
        print vecStr
        feaVecFile = open("featureVectors.txt", "a")
        feaVecFile.write(vecStr)
        feaVecFile.close()
        
    def getTFIDFVec(self):
        print "aa"

#process each file
def processFile(filename):
    global docCardinality, docList, tokenList
    
    infile = open(filename, "r")
    soup = BeautifulSoup(infile, "xml") #must explicitly 

    entries = soup.find_all('REUTERS')  #capital sensitive
    docCardinality += len(entries)

    for entry in entries:
        text = entry.find("TEXT")
        if text is None: continue
        
        topicText = titleText = bodyText = ""
        topic = entry.TOPICS
        if topic is not None: topicText = topic.getText()
        title = text.TITLE
        if title is not None: titleText = title.getText()
        body = text.BODY      
        if body is not None: bodyText = body.getText()

        doc = Doc(topicText, titleText, bodyText)
        docList.append(doc)
        tokenList = tokenList.union(doc.getAllTokens())
    
if __name__ == "__main__":
    for file in os.listdir("Data"):
        processFile("Data/" + file)

    
            
    