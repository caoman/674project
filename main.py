# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Sep 4, 2013

@author: lilong,man
'''
import nltk, string, os, math
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from nltk.corpus import stopwords
#from nltk import PorterStemmer
from bs4 import BeautifulSoup

#docCardinality = 0  #record the number of doc files in total
docList = []
tokenList = set()
tokenIDF = {}

def filterToken(token):
    for c in token:
        if c.isalpha():
            return True
    return False

class Doc:
    sentences = []
    
    def __init__(self, id, topics, title, text):
        self.id = id
        self.topics = topics
        self.title = title
        self.tokens = self.__tokenizeText(text)
        self.freqVec = None
        self.tfidfVec = None

    #compute the tokens for all sentences, remove stop words, punctuation, stemming and lemmatization, to lowercase 
    def __tokenizeText(self, text):
        sents = sent_tokenize(text)
        tokens = [token for sent in sents for token in word_tokenize(sent) if token not in stopwords.words('english') and string.punctuation.find(token) == -1 and filterToken(token)]
        #stemmer = nltk.stem.porter.PorterStemmer()
        #stemmer = nltk.stem.snowball.EnglishStemmer()
        lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
        #tokens = map(lambda token: lmtzr.lemmatize(stemmer.stem(token.lower())), tokens)
        
        #first do pos-tagging, then use the tag to do lemmatization.
        # available tags for wordnet: http://wordnet.princeton.edu/man/morphy.7WN.html
        
        # Must first convert token to lowercase, in order to make wordnet work properly
        tokens = map(lambda token: lmtzr.lemmatize(token.lower(), 'v'), tokens)
        return tokens
    
    def getFreqVec(self):
        if self.freqVec is not None:
            return self.freqVec
        tokens = self.tokens
        freqVec = {}
        for token in tokens:
            if freqVec.has_key(token):
                freqVec[token] += 1
            else:
                freqVec[token] = 1
        
        titleWords = self.__tokenizeText(self.title)
        #a simple function to determine the weight of a title word, just based on the length of the document
        titleWeight = int(len(tokens) * 0.05)


        for k in freqVec.keys():
            if k in titleWords:
                freqVec[k] += titleWeight
            if freqVec[k]==1:
                del freqVec[k]

        self.freqVec = freqVec
        return freqVec
    """    
    def outputFreqVec(self):
        freqVec = self.getFreqVec()
        vecStr  = self.topic + "\n{" + ",".join([key + ":" + str(val) for key, val in freqVec.iteritems()]) + "}\n" 
        print vecStr
        feaVecFile = open("featureVectors.txt", "a")
        feaVecFile.write(vecStr)
        feaVecFile.close()
    """ 
    def getTFIDFVec(self):
        global tokenIDF
        if self.tfidfVec is not None:
            return self.tfidfVec
        if len(tokenIDF)==0:
            print 'IDF has not been computed!'
            return

        max_freq = 1
        tfidfVec = {}
        freqVec = self.getFreqVec()
        for v in freqVec.itervalues():
            if v>max_freq:
                max_freq=v

        tokens = self.tokens
        #cardi_d = float(len(tokens))
        for token, freq in freqVec.iteritems():
            tf = 0.5 + (0.5*freq)/max_freq
            tfidf = tf * tokenIDF[token]
            tfidfVec[token] = tfidf

        self.tfidfVec = tfidfVec
        return tfidfVec

def computeIDF():
    global tokenIDF, docList, tokenList
    
    print "Computing global IDF..."
    if len(tokenIDF)>0: return
    cardi_D = float(len(docList))
    for t in tokenList:
        count_d = 0
        for doc in docList:
            if t in doc.tokens:
                count_d += 1
        tokenIDF[t] = math.log10(cardi_D / count_d)
        #tokenIDF[t] = 1

#output vector
def outputVec(outfile, vector, prefix):
    vecStr = prefix + "\n{" + ",".join([key + ":" + str(val) for key, val in vector.iteritems()]) + "}\n"
    #vecStr = prefix + "\n" + str(vector) + "\n"
    print vecStr
    outfile.write(vecStr)

#process each file
def processFile(filename, outfile):
    global docList, tokenList
    
    preTag = "<REUTERSList>"
    posTag = "</REUTERSList>"
    infile = open(filename, "r")
    firstLine = infile.readline()
    fileContent = infile.read()
    fileContent = firstLine + preTag + fileContent + posTag
    
    soup = BeautifulSoup(fileContent, "xml") #must explicitly 
    entries = soup.find_all("REUTERS")  #capital sensitive
    #docCardinality += len(entries)

    infile.close()
    print len(entries)
    for entry in entries:
        text = entry.find("TEXT")
        if text is None: continue
        
        titleText = bodyText = ""
        #topics=[]
        #if entry.get('TOPICS')!="NO":
        topics = [t.getText() for t in entry.TOPICS.find_all('D')]
        title = text.TITLE
        if title is not None: titleText = title.getText()
        body = text.BODY      
        if body is not None: bodyText = body.getText()
        
        id = entry.get('NEWID')

        doc = Doc(id, topics, titleText, bodyText)
        docList.append(doc)
        tokenList = tokenList.union(doc.tokens)
        outputVec(outfile, doc.getFreqVec(), doc.id + " "+ str(doc.topics))
    
if __name__ == "__main__":
    dirPrefix='Data/'
    #dirPrefix = '/home/0/srini/WWW/674/public/reuters/'
    #nltk.download()
    feaVecFile = open("freqVectors.txt", "w") 
    for file in os.listdir(dirPrefix):
        #print file
        processFile(dirPrefix + file, feaVecFile)
        #break
    #print tokenList
    feaVecFile.close()

    tfidfFile = open("tfidfVectors.txt", "w")
    computeIDF()
    for doc in docList:
        outputVec(tfidfFile, doc.getTFIDFVec(), doc.id)
    tfidfFile.close()
    
