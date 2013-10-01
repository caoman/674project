# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Sep 18, 2013

@author: lilong, man
'''
import re, os, math, random, heapq, operator, time

docList = []
trainDocList = []
testDocList = []
valFold = 5     #4:1 cross validation
numTopics = 2   #Number of topics per doc predicted by classification algorithm. If it's 1, the effect is equivalent to the old code.
allWords = set()


class Doc:
    def __init__(self, topics, feaVec):
        self.topics = topics
        self.feaVec = feaVec
        for w in feaVec.iterkeys():
            allWords.add(w)

class TopicClass:
    def __init__(self, doc, topic):
        self.docList = []
        self.topic = topic
        self.wordCnt = 0
        # mapping of word : docs that contain the word
        self.wordDocVec = {}
        self.addDoc(doc)
    
    def addDoc(self, doc):
        self.docList.append(doc)
        for token, val in doc.feaVec.iteritems():
            self.wordCnt += val
            if self.wordDocVec.has_key(token): self.wordDocVec[token] += 1
            else: self.wordDocVec[token] = 1


#tested
#The heap records the top-K docs in the training set with largest similarities with the current test doc
#It is a min-heap
class Heap:
    def __init__(self, maxSize):
        self.heap = []
        self.maxSize = maxSize
    
    def push(self, sim, topics):
        curHeapSize = len(self.heap)
        
        if curHeapSize < self.maxSize:            
            self.heap.append((sim, topics))        #python just implemented the min-heap
            if curHeapSize == self.maxSize - 1:
                heapq.heapify(self.heap)
        elif self.heap[0][0] < sim:
            heapq.heapreplace(self.heap, (sim, topics))
                 

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
    
def calCosSim(vec1, vec2):          # the larger, the more similar
    numerator = 0
    denominator1 = denominator2 = 0
    
    for token, val in vec1.iteritems():
        denominator1 += val * val
        if vec2.has_key(token):
            numerator += val * vec2[token]
    
    for val in vec2.itervalues():
        denominator2 += val * val
    
    if denominator1 == 0 or denominator2 == 0: return 0    
    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2)) 

def isRelated(doc, topicDict):
    global numTopics

    #sort the topics in descending order according to the values
    sortedTopicDict = sorted(topicDict.iteritems(), key=operator.itemgetter(1), reverse=True)
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
    
    K = selectK()
    
    relCnt = 0
    testDocSize = len(testDocList)
    
    for testDoc in testDocList:
        heap = Heap(K)
        for trainDoc in trainDocList:
            sim = calCosSim(testDoc.feaVec, trainDoc.feaVec)
            heap.push(sim, trainDoc.topics)
        
        topicDict = {}
        
        for tuple in heap.heap:
            for topic in tuple[1]:
                if topicDict.has_key(topic):
                    topicDict[topic] += 1
                else:
                    topicDict[topic] = 1
        
        if isRelated(testDoc, topicDict):
            relCnt += 1
    precision = float(relCnt) / testDocSize
    print "KNN Precision:" + str(precision)
      
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
            if classDict.has_key(docTopic):
                classDict[docTopic].addDoc(doc)
            else:
                classDict[docTopic] = TopicClass(doc, docTopic)
    
        for w in doc.feaVec.iterkeys():
            if wordDocFreq.has_key(w): wordDocFreq[w] += 1
            else: wordDocFreq[w] = 1

    endTime = time.time()
    print "Bayes Training time: " + str(endTime - startTime)
    topicDict = {}
    relCnt = 0
    
    startTime = time.time()
    for doc in testDocList:
        for topicClass in classDict.itervalues():
            priorProb = float(len(topicClass.docList)) / docCnt
            itemsProb = 1
            for token in doc.feaVec.keys():
                if wordDocFreq.has_key(token):
                    bayesP = float(wordDocFreq[token]) / len(trainDocList)
                else:
                    bayesP = 0.01 / len(trainDocList)
                itemOcc = bayesM * bayesP
                if topicClass.wordDocVec.has_key(token):
                    itemOcc += topicClass.wordDocVec[token]
                itemsProb *= float(itemOcc) / (len(topicClass.docList) + bayesM)
            tmpProb = itemsProb * priorProb
            topicDict[topicClass.topic] = tmpProb
        if isRelated(doc, topicDict):
            relCnt += 1
    
    endTime = time.time()

    print "Bayes Testing time: " + str((endTime - startTime)/float(len(testDocList)))
    precision = float(relCnt) / len(testDocList)
    print "Bayes precision:" + str(precision)

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
            
        #classifyWithKNN()
        classifyWithBayes()
        #classifyWithBayes2()
        
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    crossValidate() 
    
    
    
