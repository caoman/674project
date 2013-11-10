'''
Created on Nov 3, 2013

@author: lilong
'''
import time
from helperFunctions import calSkew, calEntropy, calCosSim, calJaccard

docList = [] 
clusterCntList = [2, 3, 4, 5, 6, 7] #the clusters we want
proxList = []       #the distance between different docs
startIndex = 0      #describe the start searching index for the min dis in proxList

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
    global proxList
    global startIndex
    
    clusterCnt = len(docList)
    while clusterCnt > 1:
        minDis = 1.1
        
        subList = proxList[startIndex:]
        for tuple in subList:
            cluster1 = docList[tuple[0]].cluster
            cluster2 = docList[tuple[1]].cluster 
            if cluster1 != cluster2:
                minDis = tuple[2]
                break
            startIndex += 1
        
        #combine clusters
        newCluster = Cluster()
        newCluster.distance = minDis
        newCluster.docList = cluster1.docList + cluster2.docList
        newCluster.clusterList.append(cluster1)
        newCluster.clusterList.append(cluster2)
        
        for doc in cluster1.docList:
            doc.cluster = newCluster
        for doc in cluster2.docList:
            doc.cluster = newCluster
        clusterCnt -= 1
        print "clusterCnt:" + str(clusterCnt)

#n is the number of cluster we want
def getClusters(n):    
    clusters = []
    clusterCnt = 1
    clusters.append(docList[0].cluster)
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
        doc.cluster = cluster
        
        index += 1

#measureFlag = 0: cosine, measureFlag = 1: Jaccard
def computeProxList(measureFlag):
    global proxList
    
    for index, doc in enumerate(docList[:-1]):
        afDocs = docList[index+1: ]
        for afIndex, afDoc in enumerate(afDocs):
            if measureFlag == 0:
                proxVal = calCosSim(doc.feaVec, afDoc.feaVec)
            else:
                proxVal = calJaccard(doc.feaVec, afDoc.feaVec)
            proxList.append((index, afIndex + index + 1, 1 - proxVal))
        print "calProx for doc" + str(index)
    proxList.sort(key = lambda tuple: tuple[2])
    #print proxList

def freeMemory():
    global proxList
    global docList
    
    del proxList
    proxList = []
    
    for doc in docList:        
        cluster = Cluster()
        cluster.docList.append(doc)
        del doc.cluster
        doc.cluster = cluster

def printProxList(measureFlag):
    global proxList
    if measureFlag == 0: matrixFile = open("cosMatrix.txt", "w")
    if measureFlag == 1: matrixFile = open("jacMatrix.txt", "w")
    
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
        printProxList(measureFlag)
        
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

        
    