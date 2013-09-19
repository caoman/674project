# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Sep 4, 2013

@author: lilong, man
'''
import nltk, string, os, math, sys
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk.corpus import wordnet

docList = []        #the number of docs in the corpus
tokenList = set()   #the number of tokens in the corpus
tokenIDF = {}       #the IDF value of each word in the corpus
synonymDic = {}     #the synonym dictionary for the token
procDocCnt = None   #the number of docs to be processed in each file

def containsAlpha(token):
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
    
    def __init__(self, id, topics, title, places, text):
        self.id = id
        self.topics = topics
        self.title = title
        self.places = places
        self.tokens = self.__tokenizeText(text)
        self.freqVec = None
        self.tfidfVec = None

    def __tokenizeText(self, text):
        sents = sent_tokenize(text)
        tokenSents = [word_tokenize(sent) for sent in sents]
        taggedSents = nltk.tag.batch_pos_tag(tokenSents)
        lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
        
        #lemmatization
        tokens = []
        #for taggedToken in taggedTokens:
        for sent in taggedSents:
            for taggedToken in sent:
                token = taggedToken[0].lower()
                #remove stop words, punctuation, numbers, and single character
                if len(token) > 1 and token not in stopwords.words('english') and string.punctuation.find(token) == -1 and containsAlpha(token):
                    pos = getWordNetPos(taggedToken[1])
                    if pos is not None: tokens.append(lmtzr.lemmatize(token, pos))
        
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
        titleWeight = int(1 + len(tokens) * 0.05)

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
    vecStr = prefix + "\n{" + ",".join(["'" + key + "'" + ":" + str(val) for key, val in vector.iteritems()]) + "}\n"
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
    
    #entries = soup.find_all("REUTERS", limit = int(procDocCnt))  #capital sensitive
    entries = soup.find_all("REUTERS")  #capital sensitive
    
    infile.close()
    for entry in entries:
        text = entry.find("TEXT")
        if text is None: continue
        
        titleText = bodyText = ""
        topics = ";".join([t.getText() for t in entry.TOPICS.find_all('D')])
        if len(topics) == 0:
            topics = "None"
        places = ";".join([p.getText() for p in entry.PLACES.find_all('D')])
        if len(places) == 0:
            places = "None"        
        title = text.TITLE
        if title is not None: titleText = title.getText()
        body = text.BODY      
        if body is not None: bodyText = body.getText()
        
        id = entry.get("NEWID")
        print id
        #titleText is also considered as part of bodyText, in case the bodyText is empty.
        doc = Doc(id, topics, titleText, places, titleText + "." + bodyText)
        docList.append(doc)
        tokenList = tokenList.union(doc.tokens)
        
        docInfo = "NEWID:" + doc.id + " TOPICS:" + doc.topics + " PLACES:" + doc.places 
        #docInfo = "{'NEWID':" + doc.id + " ,'TOPICS':" + doc.topics + " ,'PLACES':" + doc.places + "}"
        outputVec(outfile, doc.getFreqVec(), docInfo)
    
if __name__ == "__main__":
    #dirPrefix = "Data/"
    dirPrefix = '/home/0/srini/WWW/674/public/reuters/'
    #downloads the necessary packages
    nltk.download("maxent_treebank_pos_tagger")
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("wordnet")
    
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        procDocCnt = sys.argv[1]
    
    #feaVecFile = open("TrainFreqVectors.txt", "w") 
    print "Computing Train Frequency vector..."
    baseName = "freqVector"
    fileNum = 0
    for file in os.listdir(dirPrefix):
        fileNum += 1
        feaVecFile = open(baseName + str(fileNum) + ".txt", "w")
        processFile(dirPrefix + file, feaVecFile)
        feaVecFile.close()
    print "Frequency vector is done!"

    #tfidfFile = open("TraintfidfVectors.txt", "w")
    print "Computing Train TFIDF vector..."
    computeIDF()

    baseName = "tfidfVector"
    fileNum = 0
    tfidfFile = open(baseName + str(fileNum) + ".txt", "w")
    for doc in docList:
        fileNum += 1
        docInfo = "NEWID:" + doc.id + " TOPICS:" + doc.topics + " PLACES:" + doc.places 
        outputVec(tfidfFile, doc.getTFIDFVec(), docInfo)
    tfidfFile.close()
    print "TFIDF vector is done!"
    
