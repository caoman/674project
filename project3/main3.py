# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Nov 3, 2013

@author: lilong
'''
import math
from helperFunctions import *

docList = [] 
clusterList = []
proxMatrix = []     #store the distance
docIndexCluster = []    #record doc belongs to which cluster
clusterCntList = [2, 4, 6, 8, 10]

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
    global proxMatrix
    
    clusterCnt = len(clusterList)
    while clusterCnt > 1:
        minDis = 1.1            #the maximum value of distance is 1
        minRowIndex = 0
        minColIndex = 0
        
        for rowIndex, disRow in enumerate(proxMatrix):
            for colIndex, dis in enumerate(disRow):
                if dis < minDis: 
                    minDis = dis
                    minRowIndex = rowIndex
                    minColIndex = colIndex
        
        #update matrix set
        docIndex1 = minRowIndex
        docIndex2 = minRowIndex + minColIndex + 1
        cluster1 = clusterList[docIndexCluster[docIndex1]]
        cluster2 = clusterList[docIndexCluster[docIndex2]]
        for doc1 in cluster1.docList:
            docIndex1 = doc1.index
            for doc2 in cluster2.docList:
                docIndex2 = doc2.index
                if docIndex1 < docIndex2:
                    proxMatrix[docIndex1][docIndex2 - docIndex1 - 1] = 1.1
                else:
                    proxMatrix[docIndex2][docIndex1 - docIndex2 - 1] = 1.1
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
        printCluster(newCluster)
        
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
        cluster.index = doc.index
        clusterList.append(cluster)
        
        docIndexCluster.append(index)
        
        index += 1

def computeProxMatrix():
    global proxMatrix

    for index, doc in enumerate(docList[:-1]):
        proxMatrix.append([])
        afDocs = docList[index+1: ]
        for afDoc in afDocs:
            cosVal = calCosSim(doc.feaVec, afDoc.feaVec)
            proxMatrix[index].append(1 - cosVal)
            
def printProxMatrix():
    global proxMatrix
    for row in proxMatrix:
        rowStr = ""
        for cell in row:
            rowStr += str(cell) + " "
        print rowStr 

def printCluster(cluster):
    print "dis:" + str(cluster.distance)
    for subCluster in cluster.clusterList:
        docStr = ""
        for doc in subCluster.docList:
            docStr += doc.newsID + " "
        print docStr
    
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    computeProxMatrix()
    printProxMatrix()
    hierachCluster()
    print "return the certain number of clusters"
    for clusterCnt in clusterCntList:
        clusters = getClusters(clusterCnt)
        print "clusters:"
        for cluster in clusters:
            print [doc.newsID for doc in cluster.docList]
        print "entropy:" + str(calEntropy(clusters))
        print "skew:" + str(cal)

        
    
