# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Sep 4, 2013

@author: lilong,man
'''
import nltk, string, os, math
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk.corpus import wordnet

docList = []        #the number of docs in the corpus
tokenList = set()   #the number of tokens in the corpus
tokenIDF = {}       
synonymDic = {}     #the synonym dictionary for the token

def isNum(token):
    for c in token: 
        if c.isalpha(): 
            return True
    return False

#map the pos tag in treebank to the pos tag in wordnet, only verb, adjective, adverb, noun are left
def getWordNetPos(treebankPos):
    if treebankPos.startswith("NN"): return "n"
    elif treebankPos.startswith("JJ"): return "a"
    elif treebankPos.startswith("RB"): return "r"
    elif treebankPos.startswith("VB"): return "v"
    else: return None

def getSynonyms(word):
    global synonymDic
    if synonymDic.has_key(word): return synonymDic[word]
    synonyms = [lemma for syn in wordnet.synsets(word) for lemma in syn.lemma_names]
    synonymDic[word] = synonyms
    return synonyms

class Doc:
    sentences = []
    
    def __init__(self, id, topics, title, text):
        self.id = id
        self.topics = topics
        self.title = title
        self.tokens = self.__tokenizeText(text)
        self.freqVec = None
        self.tfidfVec = None

    def __tokenizeText(self, text):
        sents = sent_tokenize(text)
        #remove stop words, punctuation, and numbers
        tokens = [token for sent in sents for token in word_tokenize(sent) if token not in stopwords.words('english') and string.punctuation.find(token) == -1 and isNum(token)]
        taggedTokens = nltk.pos_tag(tokens)
        lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
        
        #lemmatization
        tokens = []
        for taggedToken in taggedTokens:
            pos = getWordNetPos(taggedToken[1])
            if pos is not None: tokens.append(lmtzr.lemmatize(taggedToken[0].lower(), pos))
        
        #merge the synonym tokens
        tokensLength = len(tokens)
        for index, token in enumerate(tokens):
            for i in range(index + 1, tokensLength):
                synonyms = getSynonyms(token)
                if tokens[i] in synonyms: tokens[i] = token
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
                del freqVec[k]      #the tokens with low frequency are delete

        self.freqVec = freqVec
        return freqVec

    def getTFIDFVec(self):
        global tokenIDF
        if self.tfidfVec is not None:
            return self.tfidfVec
        if len(tokenIDF) == 0: 
            return

        max_freq = 1
        tfidfVec = {}
        freqVec = self.getFreqVec()
        for v in freqVec.itervalues():
            if v>max_freq:
                max_freq=v

        for token, freq in freqVec.iteritems():
            tf = 0.5 + (0.5 * freq) / max_freq
            tfidf = tf * tokenIDF[token]
            tfidfVec[token] = tfidf

        self.tfidfVec = tfidfVec
        return tfidfVec

def computeIDF():
    global tokenIDF, docList, tokenList
    
    if len(tokenIDF)>0: return
    cardi_D = float(len(docList))
    for t in tokenList:
        count_d = 0
        for doc in docList:
            if t in doc.tokens:
                count_d += 1
        tokenIDF[t] = math.log10(cardi_D / count_d)

#output vector
def outputVec(outfile, vector, prefix):
    vecStr = prefix + "\n{" + ",".join([key + ":" + str(val) for key, val in vector.iteritems()]) + "}\n"
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

    infile.close()
    for entry in entries:
        text = entry.find("TEXT")
        if text is None: continue
        
        titleText = bodyText = ""
        topics = ";".join([t.getText() for t in entry.TOPICS.find_all('D')])
        title = text.TITLE
        if title is not None: titleText = title.getText()
        body = text.BODY      
        if body is not None: bodyText = body.getText()
        
        id = entry.get("NEWID")
        doc = Doc(id, topics, titleText, bodyText)
        docList.append(doc)
        tokenList = tokenList.union(doc.tokens)
        outputVec(outfile, doc.getFreqVec(), doc.id + " " + str(doc.topics))
    
if __name__ == "__main__":
    dirPrefix= "Data/"
    #dirPrefix = '/home/0/srini/WWW/674/public/reuters/'
    #downloads the necessary packages
    nltk.download("maxent_treebank_pos_tagger")
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("wordnet")
    
    feaVecFile = open("freqVectors.txt", "w") 
    print "Computing Frequency vector..."
    for file in os.listdir(dirPrefix):
        processFile(dirPrefix + file, feaVecFile)
    feaVecFile.close()
    print "Frequency vector is done!"

    tfidfFile = open("tfidfVectors.txt", "w")
    print "Computing TFIDF vector..."
    computeIDF()
    for doc in docList:
        outputVec(tfidfFile, doc.getTFIDFVec(), doc.id + " " + str(doc.topics))
    tfidfFile.close()
    print "TFIDF vector is done!"
    
