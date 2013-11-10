'''
Created on Nov 3, 2013

@author: lilong
'''
import math, time
from helperFunctions import calSkew, calEntropy, calCosSim, calJaccard

docList = [] 
clusterList = []
flagMatrix = []     #indicate whether two documents are in the same cluster
docIndexCluster = []    #record doc belongs to which cluster
clusterCntList = [2, 4, 8, 16, 32, 64]
proxList = []
startIndex = 0      #describe the starting index for the min dis

class Cluster:
    def __init__(self):
        self.distance = 0
        self.clusterList = [] 
        self.docList = []   

class Doc:
    def __init__(self, topics, feaVec, index, newsID):
        self.topics = topics
        self.feaVec = feaVec
        self.index = index
        self.newsID = newsID
               
def hierachCluster():
    global flagMatrix
    global proxList
    global startIndex
    
    clusterCnt = len(clusterList)
    while clusterCnt > 1:
        docIndex1 = 0
        docIndex2 = 0
        minDis = 1.1
        
        subList = proxList[startIndex:]
        for tuple in subList:
            docIndex1 = tuple[0]
            docIndex2 = tuple[1]
            if flagMatrix[docIndex1][docIndex2 - docIndex1 - 1] == 0:
                minDis = tuple[2]
                break
            startIndex += 1
        #print "docIndex1:" + str(docIndex1) + " docIndex2:" + str(docIndex2)
        #update matrix set
        cluster1 = clusterList[docIndexCluster[docIndex1]]
        cluster2 = clusterList[docIndexCluster[docIndex2]]
        for doc1 in cluster1.docList:
            docIndex1 = doc1.index
            for doc2 in cluster2.docList:
                docIndex2 = doc2.index
                if docIndex1 < docIndex2:
                    flagMatrix[docIndex1][docIndex2 - docIndex1 - 1] = 1
                else:
                    flagMatrix[docIndex2][docIndex1 - docIndex2 - 1] = 1
        #printProxMatrix()
        
        #assign the new mapping relationship between documents and clusters
        for index in range(len(docIndexCluster)):
            if docIndexCluster[index] > docIndexCluster[docIndex2]:
                docIndexCluster[index] -= 1
        for doc in cluster2.docList:
            docIndexCluster[doc.index] = docIndexCluster[docIndex1]
        
        #combine clusters
        newCluster = Cluster()
        newCluster.distance = minDis
        newCluster.docList = cluster1.docList + cluster2.docList
        newCluster.clusterList.append(cluster1)
        newCluster.clusterList.append(cluster2)
        clusterList.remove(cluster2)
        clusterList[docIndexCluster[docIndex1]] = newCluster
        print "clusterCnt:" + str(clusterCnt)
        #printCluster(newCluster)
        
        clusterCnt = len(clusterList)

#n is the number of cluster we want
def getClusters(n):
    global clusterList
    
    clusters = []
    clusterCnt = 1
    clusters.append(clusterList[0])
    while clusterCnt < n:   
        maxDis = -0.1
        maxDisClusters = []
        
        for cluster in clusters:
            if len(cluster.clusterList) > 0 and cluster.distance >= maxDis:
                maxDis = cluster.distance
                maxDisClusters.append(cluster)
        
        for maxCluster in maxDisClusters:
            clusters += maxCluster.clusterList
            clusters.remove(maxCluster)
        clusterCnt = len(clusters)
    return clusters
   
 
#Read the input file and store the vectors in the memory
def readVectors(fileName):
    global docList
    global clusterList
    vecFile = open(fileName, 'r')
    index = 0
    
    while True:
        metaData = vecFile.readline() 
        if len(metaData) == 0: break
        metaVec = eval(metaData)
        vec = eval(vecFile.readline())    
        doc = Doc(metaVec['TOPICS'], vec, index, metaVec['NEWID'])
        docList.append(doc)
        
        cluster = Cluster()
        cluster.docList.append(doc)
        clusterList.append(cluster)
        
        docIndexCluster.append(index)
        
        index += 1

#measureFlag = 0: cosine, measureFlag = 1: Jaccard
def computeProxList(measureFlag):
    global proxList
    global flagMatrix
    
    for index, doc in enumerate(docList[:-1]):
        flagMatrix.append([])
        afDocs = docList[index+1: ]
        for afIndex, afDoc in enumerate(afDocs):
            if measureFlag == 0:
                proxVal = calCosSim(doc.feaVec, afDoc.feaVec)
            else:
                proxVal = calJaccard(doc.feaVec, afDoc.feaVec)
            flagMatrix[index].append(0)
            proxList.append((index, afIndex + index + 1, 1 - proxVal))
    proxList.sort(key = lambda tuple: tuple[2])
    #print proxList

def freeMemory():
    global flagMatrix
    global proxList
    global clusterList
    global docList
    global docIndexCluster
    
    del proxList
    proxList = []
    
    for row in flagMatrix:
        del row
    del flagMatrix
    flagMatrix = []
        
    clusterQueue = []
    clusterQueue += clusterList
    while len(clusterQueue) > 0:
        cluster = clusterQueue.pop()
        clusterQueue += cluster.clusterList
        del cluster
    del clusterList
    clusterList = []
    
    del docIndexCluster
    docIndexCluster = []
    for doc in docList:        
        cluster = Cluster()
        cluster.docList.append(doc)
        clusterList.append(cluster)
        docIndexCluster.append(doc.index)

def printProxList(measureFlag):
    global proxList
    if measureFlag == 0: matrixFile = open("cosMatrix.txt", "w")
    if measureFlag == 1: matrixFile = open("jaccard.txt", "w")
    
    matrixFile.write(str(proxList))
    matrixFile.close()

def printCluster(cluster):
    print "dis:" + str(cluster.distance)
    for subCluster in cluster.clusterList:
        docStr = ""
        for doc in subCluster.docList:
            docStr += doc.newsID + " "
        print docStr
    
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    resultFile = open("Result.txt", "w")
    
    for measureFlag in [0, 1]:
        startTime = time.time()
        computeProxList(measureFlag)
        endTime = time.time()
        resultFile.write("Time for computing the matrix:" + str(endTime - startTime) + "\n") 
        resultFile.flush()
        #printProxList(measureFlag)
        
        startTime = time.time()
        hierachCluster()
        endTime = time.time()
        resultFile.write("Time for clustering all documents:" + str(endTime - startTime) + "\n")
        resultFile.flush()
        for clusterCnt in clusterCntList:
            clusters = getClusters(clusterCnt)
            resultFile.write("Time for " + str(clusterCnt) + " clusters:" + str(endTime - startTime) + "\n")
            resultFile.write("entropy:" + str(calEntropy(clusters)) + " " + "skew:" + str(calSkew(clusters)) + "\n")
            endTime = time.time()
            resultFile.write("clusters" + "\n")
            for cluster in clusters:
                resultFile.write(str([doc.newsID for doc in cluster.docList]) + "\n")
        resultFile.write("==========================================\n")
        freeMemory()
        resultFile.flush()
    resultFile.close()

        
    