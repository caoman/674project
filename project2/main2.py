'''
Created on Sep 18, 2013

@author: lilong, man
'''
import re, os, math, random
from collections import deque

classDocList = []
trainDocList = deque()
testDocList = deque()
classDict = {}
valFold = 5     #4:1 cross validation
trainDocCnt = 0
testDocCnt = 0

class Doc:
    def __init__(self, topics, feaVec):
        self.topics = topics
        self.feaVec = feaVec

class topicClass:
    def __init__(self, doc):
        self.centroidVec = {}
        self.docList = []
        self.topic = doc.topics[0]
        self.addDoc(doc)   
        self.docCnt = 0
    
    def addDoc(self, doc):
        self.docList.append(doc)
        for token, val in doc.feaVec.iteritems():
            if self.centroidVec.has_key(token):  self.centroidVec[token] += val
            else: self.centroidVec[token] = val

    #maybe need to delete the tokens with low freq
    def setCentroid(self):
        self.docCnt = len(self.docList)
        for token, val in self.centroidVec.iteritems():
            self.centroidVec[token] = float(val) / self.docCnt 

def readVectors(fileName):
    global classDocList
    vecFile = open(fileName, 'r')
    
    while True:
        metaData = vecFile.readline() 
        if len(metaData) == 0: break
        metaVec = eval(metaData)
        vec = eval(vecFile.readline())    
        doc = Doc(metaVec['TOPICS'], vec)
        classDocList.append(doc)

def spliteDocs():
    global classDocList
    partSize = int(math.ceil(len(classDocList) / valFold))
    
    for i in range(valFold - 1):
        trainDocList.append(classDocList[i * partSize: (i + 1) * partSize])
    trainDocCnt = (valFold - 1) * partSize
    
    testDocList.append(classDocList[trainDocCnt:])
    testDocCnt = len(classDocList) - trainDocCnt 
    
def calCosSim(vec1, vec2):
    numerator = 0
    denominator1 = denominator2 = 0
    
    for token, val in vec1.iteritems():
        denominator1 += val * val
        if vec2.has_key(token):
            numerator += val * vec2[token]
    
    for val in vec2.itervalues():
        denominator2 += val * val
        
    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2)) 

#firstly form the classes with the docs with only one topic
#then assign the docs with multiple topics into the compatible classes    
def classify():
    printTrainTest()
    #build the model
    global trainDocList
    global classDict
    
    mulTopicsDocList = []
    
    for docGroup in trainDocList:
        for doc in docGroup:
            if len(doc.topics) > 1: 
                mulTopicsDocList.append(doc)
                continue
            docTopic = doc.topics[0]
            if classDict.has_key(docTopic):
                classDict[docTopic].addDoc(doc)
            else:
                topicClass = topicClass(doc)
                classDict[docTopic] = topicClass
        
    for doc in mulTopicsDocList:
        for classTopic, knnClass in classDict.iteritems():
            if classTopic in doc.topics:
                knnClass.addDoc(doc)
    
    #classifyWithKNN
    for topicClass in classDict.itervalues():
        topicClass.setCentroid()
    
    '''for topicClass, knnClass in classDict.iteritems():
        print topicClass
        print knnClass.centroidVec'''
    relCnt = 0              #record the correct classified docs
    
    for docGroup in testDocList:
        for doc in docGroup:
            sim = 0
            docClass = None
            
            for knnClass in classDict.itervalues():
                topicVec = knnClass.centroidVec
                tmpSim = calCosSim(doc.feaVec, topicVec)
                print knnClass.topic + " " + str(tmpSim)
                if tmpSim > sim:
                    sim = tmpSim
                    docClass = knnClass.topic
            
            #if the cosin similarity between the doc and all the classes is 0, then we assign the doc to one certain class randomly
            if docClass is None: docClass = random.choice(classDict.keys())
            if docClass in doc.topics:
                relCnt += 1
            
            print docClass + " " + str(doc.topics)
            
    precision = float(relCnt) / testDocCnt
    print "KNN precision:" + str(precision)
    
    #classify with naive Bayes
    relCnt = 0
    
    for docGroup in testDocList:
        for doc in docGroup:
            docClass = None
            prob = 0
            for topicClass in classDict.itervalues():
                priorProb = float(topicClass.docCnt) / trainDocCnt
                itemsProb = 1
                for token in doc.feaVec.keys():
                    itemOcc = 0
                    for classDoc in topicClass.docList:
                        if classDoc.feaVec.has_key(token):
                            itemOcc += 1
                    itemsProb *= float(itemOcc) / topicClass.docCnt
                tmpProb = itemsProb * priorProb
                if tmpProb > prob:
                    prob = tmpProb
                    docClass = topicClass.topic
            
            if docClass in doc.topics:
                relCnt += 1
    
    precision = float(relCnt) / testDocCnt
    print "Bayes precision:" + precision   

def crossValidate():
    for i in range(valFold):
        #printTrainTest()
        classify()
        
        trainDocList.append(testDocList.popleft())
        testDocList.append(trainDocList.popleft())
        break
        
        
def printTrainTest():
    global trainDocList
    global testDocList
    print "--------------------------------"
    print "trainDocList"
    for trainDocs in trainDocList:
        print "one group"
        for doc in trainDocs:
            print doc.topics 
            print doc.feaVec
    print "testDocList"
    for testDocs in testDocList:
        print "one group"
        for doc in testDocs:
            print doc.topics 
            print doc.feaVec
  
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    spliteDocs()
    crossValidate()
    '''for doc in classDocList:
        print doc.topics
        print doc.feaVec'''   
    
    
    
