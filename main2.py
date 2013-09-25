'''
Created on Sep 18, 2013

@author: lilong, man
'''
import re, os, math
from collections import deque

classDocList = []
trainDocList = deque()
testDocList = deque()
knnClassList = {}
testDocCnt = 0
valFold = 5     #4:1 cross validation

class Doc:
    def __init__(self, topics, feaVec):
        self.topics = topics
        self.feaVec = feaVec

class KNNTopicClass:
    def __init__(self, doc):
        self.centroidVec = {}
        self.docCnt = 0
        self.topic = doc.topics[0]
        self.updateCentVec(doc)
        
    def updateCentVec(self, doc):
        self.docCnt += 1
        
        for token, val in doc.feaVec.iteritems():
            if self.centroidVec.has_key(token):  self.centroidVec[token] += val
            else: self.centroidVec[token] = val
    
    def setCentroid(self):
        for token, val in self.centroidVec:
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
    
    testDocList.append(classDocList[(valFold - 1) * partSize:])

    
def calCosSim(vec1, vec2):
    numerator = 0.0
    denominator = 0
    
    for token, val in vec1.iteritems():
        denominator += val * val
        if vec2.has_key(token):
            numerator += val * vec2[token]
    
    for val in vec2.itervalues():
        denominator += val * val
        
    return numerator / denominator

#firstly form the classes with the docs with only one topic
#then assign the docs with multiple topics into the compatible classes    
def classifyWithKNN():
    #build the model
    global trainDocList
    global knnClassList
    
    mulTopicsDocList = []
    
    for docGroup in trainDocList:
        for doc in docGroup:
            if len(doc.topics) > 1: 
                mulTopicsDocList.append(doc)
                continue
            
            if knnClassList.has_key(doc.topics[0]):
                knnClassList[doc.topics[0]].updateCentVec(doc)
            else:
                topicClass = KNNTopicClass(doc)
                knnClassList.append(topicClass)   
        
    for doc in mulTopicsDocList:
        for knnClass in knnClassList:
            if knnClass.topic in doc.topics:
                knnClass.updateCentVec(doc)
    
    for topicClass in knnClassList:
        topicClass.setCentroid()
    
    for knnClass in knnClassList:
        print knnClass.centroidVec
    #test the model
    '''relCnt = 0
    
    for doc in testDocList:
        sim = -1
        docClass = ""
        
        for topicClass in knnClassList:
            topicVec = topicClass.centroidVec
            tmpSim = calCosSim(doc.feaVec, topicVec)
            if tmpSim > sim:
                sim = tmpSim
                docClass = topicClass.topic
        
        if docClass == doc.topic:
            relCnt += 1
        
    precision = float(relCnt) / testDocCnt'''
          
def crossValidate():
    for i in range(valFold):
        #printTrainTest()
        classifyWithKNN()
        
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
    
    
    
