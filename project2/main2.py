# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Sep 18, 2013

@author: lilong, man
'''
import re, os, math, random, heapq, operator, time

docList = []        #including training dataset and test dataset
trainDocList = []
testDocList = []
valFold = 5         #4:1 cross validation
numTopics = 2       #Number of topics per doc predicted by classification algorithm. 

class Doc:
    def __init__(self, topics, feaVec):
        self.topics = topics
        self.feaVec = feaVec

class TopicClass:
    def __init__(self, doc, topic):
        self.docList = []
        self.topic = topic
        self.wordCnt = 0    
        self.wordDocVec = {}    # mapping of word : the number of docs that contain the word
        self.addDoc(doc)
    
    def addDoc(self, doc):
        self.docList.append(doc)
        for token, val in doc.feaVec.items():
            self.wordCnt += val
            if token in self.wordDocVec: self.wordDocVec[token] += 1
            else: self.wordDocVec[token] = 1

#The heap records the top-K docs in the training set with largest similarities with the current test doc
#It is a min-heap
class Heap:
    def __init__(self, maxSize):
        self.heap = []
        self.maxSize = maxSize
    
    def push(self, sim, topics):
        curHeapSize = len(self.heap)
        
        if curHeapSize < self.maxSize:            
            self.heap.append((sim, topics))        
            if curHeapSize == self.maxSize - 1:
                heapq.heapify(self.heap)
        elif self.heap[0][0] < sim:
            heapq.heapreplace(self.heap, (sim, topics))
                 
#Read the input file and store the vectors in the memory
def readVectors(fileName):
    global docList
    vecFile = open(fileName, 'r')
    
    while True:
        metaData = vecFile.readline() 
        if len(metaData) == 0: break
        metaVec = eval(metaData)
        vec = eval(vecFile.readline())    
        doc = Doc(metaVec['TOPICS'], vec)
        docList.append(doc)

# the larger, the more similar
def calCosSim(vec1, vec2):         
    numerator = 0
    denominator1 = denominator2 = 0
    
    for token, val in vec1.items():
        denominator1 += val * val
        if token in vec2:
            numerator += val * vec2[token]
    
    for val in vec2.values():
        denominator2 += val * val
    
    if denominator1 == 0 or denominator2 == 0: return 0    
    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2)) 

def isRelated(doc, topicDict):
    global numTopics

    #sort the topics in descending order according to the values
    sortedTopicDict = sorted(iter(topicDict.items()), key=operator.itemgetter(1), reverse=True)
    for i in range(numTopics):
        if i < len(sortedTopicDict): 
            topic = sortedTopicDict[i][0]
            #print "predicted topic: " + topic
            #print "actual topics(s): " + str(doc.topics)
            if topic in doc.topics:
                return True
    return False

#need to consider a good way to select K
def selectK():
    global trainDocList
    return int(math.sqrt(len(trainDocList)))

def classifyWithKNN():
    global trainDocList
    global testDocList
    
    startTime = time.time()
    K = selectK()
    endTime = time.time()
    print("KNN Training time:" + str(endTime - startTime))
    
    relCnt = 0
    testDocSize = len(testDocList)
    
    startTime = time.time()
    for testDoc in testDocList:
        heap = Heap(K)
        for trainDoc in trainDocList:
            sim = calCosSim(testDoc.feaVec, trainDoc.feaVec)
            heap.push(sim, trainDoc.topics)
        
        topicDict = {}
        
        for tuple in heap.heap:
            for topic in tuple[1]:
                if topic in topicDict:
                    topicDict[topic] += 1
                else:
                    topicDict[topic] = 1
        
        if isRelated(testDoc, topicDict):
            relCnt += 1
    endTime = time.time()
    print("KNN Testing time for one document:" + str(float(endTime - startTime) / len(testDocList)))
    
    precision = float(relCnt) / testDocSize
    print("KNN Precision:" + str(precision))
      
#Not consider the count of the words, prob(w | Ci) = countDocs(contains(w), Ci) / totalDocs(Ci)
def classifyWithBayes():
    global trainDocList, testDocList
    
    bayesM = len(trainDocList)
    # mapping of word : num of docs that contain the word
    wordDocFreq = {}
    classDict = {}
    
    startTime = time.time()
    docCnt = 0
    for doc in trainDocList:
        for docTopic in doc.topics:
            docCnt += 1     # Count the doc for multiple times, if it has multiple topics
            if docTopic in classDict:
                classDict[docTopic].addDoc(doc)
            else:
                classDict[docTopic] = TopicClass(doc, docTopic)
    
        for w in doc.feaVec.keys():
            if w in wordDocFreq: wordDocFreq[w] += 1
            else: wordDocFreq[w] = 1

    endTime = time.time()
    print("Bayes Training time: " + str(endTime - startTime))
    topicDict = {}
    relCnt = 0
    
    startTime = time.time()
    for doc in testDocList:
        for topicClass in classDict.values():
            priorProb = float(len(topicClass.docList)) / docCnt
            itemsProb = 1
            for token in list(doc.feaVec.keys()):
                if token in wordDocFreq:
                    bayesP = float(wordDocFreq[token]) / len(trainDocList)
                else:   #the word doesn't occure in the training dataset
                    bayesP = 0.01 / len(trainDocList)
                itemOcc = bayesM * bayesP
                if token in topicClass.wordDocVec:
                    itemOcc += topicClass.wordDocVec[token]
                itemsProb *= float(itemOcc) / (len(topicClass.docList) + bayesM)
            tmpProb = itemsProb * priorProb
            topicDict[topicClass.topic] = tmpProb
        if isRelated(doc, topicDict):
            relCnt += 1    
    endTime = time.time()

    print("Bayes Testing time for one document: " + str((endTime - startTime)/float(len(testDocList))))
    precision = float(relCnt) / len(testDocList)
    print("Bayes precision:" + str(precision))

'''
# Consider the count of each word, prob(w | Ci) = count(w in Ci) / totalWords(Ci)
def classifyWithBayes2():
    global trainDocList, testDocList
    
    bayesM = len(trainDocList)
    classDict = {}
    
    docCnt = 0
    for doc in trainDocList:
        for docTopic in doc.topics:
            docCnt += 1
            if classDict.has_key(docTopic):
                classDict[docTopic].addDoc(doc)
            else:
                classDict[docTopic] = TopicClass(doc, docTopic)
    
    #print len(classDict)

    topicDict = {}
    relCnt = 0
    for doc in testDocList:
        for topicClass in classDict.itervalues():
            classProb = float(len(topicClass.docList)) / docCnt
            itemsProb = 1
            for token in doc.feaVec.keys():
                itemOcc = 0 + bayesM * bayesP
                if topicClass.vector.has_key(token):
                     itemOcc += topicClass.vector[token]
                itemsProb *= float(itemOcc) / (topicClass.wordCnt + bayesM)
            tmpProb = itemsProb * classProb
            topicDict[topicClass.topic] = tmpProb
        if isRelated(doc, topicDict):
            relCnt += 1
    
    precision = float(relCnt) / len(testDocList)
    print "Bayes precision:" + str(precision)
'''
def crossValidate():
    global testDocList
    global trainDocList
    
    docSize = len(docList)
    partSize = int(docSize / float(valFold) + 0.5)

    for i in range(valFold):
        startIndex = i * partSize
        endIndex = (i + 1) * partSize 
        
        if endIndex < docSize:
            testDocList = docList[startIndex: endIndex]
            trainDocList = docList[0: i * partSize] + docList[(i + 1) * partSize:]
        else:
            endIndex %= docSize
            testDocList = docList[startIndex:] + docList[0: endIndex]
            trainDocList = docList[endIndex: startIndex]
            
        classifyWithKNN()
        classifyWithBayes()
        #classifyWithBayes2()
        
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    crossValidate() 
    
    
    
