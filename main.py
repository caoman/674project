'''
Created on Sep 4, 2013

@author: lilong,man
'''
import nltk, string, os
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import PorterStemmer
#from sets import Set
from bs4 import BeautifulSoup

docCardinality = 0  #record the number of doc files in total
docList = []
tokenList = set()
tokenIDF = {}

class Doc:
    sentences = []
    
    def __init__(self, topic, title, text):
        self.topic = topic
        self.title = title
        self.text = text
	self.tokens = None 
	self.freqVec = None

    #get the tokens for all sentences, remove stop words, punctuation, stemming and lemmatization 
    def getAllTokens(self):
        if self.tokens is not None:
	    return self.tokens
	sents = sent_tokenize(self.text)
        tokens = [token for sent in sents for token in word_tokenize(sent) if token not in stopwords.words('english') and string.punctuation.find(token) == -1]
        porter = PorterStemmer()
        lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
        tokens = map(lambda token: lmtzr.lemmatize(porter.stem(token)), tokens)
        self.tokens = tokens
	return tokens
    
    def getFreqVec(self):
        if self.freqVec is not None:
	    return self.freqVec
        tokens = self.getAllTokens()
        freqVec = {}
        for token in tokens:
            if freqVec.has_key(token):
                freqVec[token] += 1
            else:
                freqVec[token] = 0
        self.freqVec = freqVec
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


def computeIDF():
    global tokenIDF
    if len(tokenIDF)>0: return
    cardi_D = len(docList)
    for t in tokenList:
        count_d = 0;
	for doc in docList:
	    if t in doc.tokens:
	        count_d += 1
        tokenIDF[t] = math.log10(cardi_D / count_d)


#process each file
def processFile(filename):
    global docCardinality, docList, tokenList
    
    infile = open(filename, "r")

    soup = BeautifulSoup(infile, "xml") #must explicitly 

    entries = soup.find_all("REUTERS")  #capital sensitive
    docCardinality += len(entries)

    print len(entries)
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
	doc.outputFreqVec()
    
if __name__ == "__main__":
    #dirPrefix='Data/'
    dirPrefix = '/home/0/srini/WWW/674/public/reuters/'
    #nltk.download()
    for file in os.listdir(dirPrefix):
	print file
        processFile(dirPrefix + file)
	break
    print tokenList
    
            
    
