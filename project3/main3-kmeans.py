# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os, math, random
docList = []

class Doc:
    def __init__(self, newid, topics, feaVec):
        self.newid = newid
        self.topics = topics
        self.feaVec = feaVec

class KmsCluster:
    def __init__(self, centroid):
        self.centroid = centroid
        self.docs = []
    def clear(self):
        del self.docs[:]
    def add(self, doc):
        self.docs.append(doc)

    #recompute centroid, and return the variation (distance) between the new centroid and old centroid
    def recomputeCentroid(self):
        newCentroid = {}
        for doc in self.docs:
            for token,val in doc.feaVec.iteritems():
                if newCentroid.has_key(token):
                    newCentroid[token] += val
                else:
                    newCentroid[token] = val
        n = len(self.docs) * 1.0
        for token,val in newCentroid.iteritems():
            newCentroid[token] = val/n
        distance = 1 - calCosSim(newCentroid, self.centroid)
        self.centroid = newCentroid
        return distance

def readVectors(fileName):
    global docList
    vecFile = open(fileName, 'r')
    
    while True:
        metaData = vecFile.readline() 
        if len(metaData) == 0: break
        metaVec = eval(metaData)
        vec = eval(vecFile.readline())    
        doc = Doc(metaVec['NEWID'], metaVec['TOPICS'], vec)
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

def getInitClusters(K):
    centroidDocs = []
    for i in range(K):
        while True:
            n = random.randint(0, len(docList)-1)
            if docList[n] not in centroidDocs:
                break
        centroidDocs.append(docList[n])
    return [KmsCluster(doc.feaVec) for doc in centroidDocs]
    
def kmeans(K, threshold):
    clusters = getInitClusters(K)
    while True:
        for doc in docList:
            sim = -1
            cluster = None
            for c in clusters:
                newSim = calCosSim(doc.feaVec, c.centroid)
                if (newSim > sim):
                    sim = newSim
                    cluster = c
            
            cluster.add(doc)
        
        maxVar = 0
        for c in clusters:
            var = c.recomputeCentroid()
            if (var > maxVar):
                maxVar = var
        if maxVar < threshold:
            break
        else:
            for c in clusters:
                c.clear()
    return clusters

def printClusters(clusters):
    for cluster in clusters:
        #print cluster.centroid
        print len(cluster.docs)
        print "#####"

if __name__ == '__main__':
    readVectors("../FreqVectors.txt")
    clusters = kmeans(4, 0.3)
    printClusters(clusters)
