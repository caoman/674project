'''
Created on Nov 3, 2013

@author: lilong
'''
import math, heapq, copy

docList = [] 
clusterList = []
proxMatrix = []     #store the distance
docIndexCluster = []    #record doc belongs to which cluster
    
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
        printProxMatrix()
        
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
                
#n is the cluster number
#def getClusters(n):
#    clusters = []
#    global clusterList
#    curCluster = clusterList[0]
#    i = 1
#    while i < n:   
   
# the larger, the more similar
def calCosSim(vec1, vec2):    
#    print vec1
#    print vec2
         
    numerator = 0
    denominator1 = denominator2 = 0
    
    for token, val in vec1.iteritems():
        denominator1 += val * val
        if vec2.has_key(token):
            numerator += val * vec2[token]
    
    for val in vec2.itervalues():
        denominator2 += val * val
    
#    print "num:" + str(numerator) + " den1:" + str(denominator1) + " den2:" + str(denominator2)
    if denominator1 == 0 or denominator2 == 0: return 0    
    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2)) 
        
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
    #print "rowCnt:" + str(len(proxMatrix))
    for row in proxMatrix:
        for cell in row:
            print str(cell) + " "
        print "\n" 
    print "------"

def printCluster(cluster):
    print "subCluserCnt:" + str(len(cluster.clusterList))
    for subCluster in cluster.clusterList:
        for doc in subCluster.docList:
            print doc.newsID + " "
        print "\n"
    
if __name__ == '__main__':
    readVectors("FreqVectors.txt")
    computeProxMatrix()
    printProxMatrix()
    hierachCluster()
    