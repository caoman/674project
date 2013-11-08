# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Nov 3, 2013

@author: man
'''
import os, math, random, time
from helperFunctions import *

docList = []
#numClusters = [2, 4, 8, 16, 32]
numClusters = [2, 4]
#calSim = calCosSim
calSim = calJaccard
Verbose = False
Threshold = 0.001

class Doc:
    def __init__(self, newid, topics, feaVec):
        self.newid = newid
        self.topics = topics
        self.feaVec = feaVec

class KmsCluster:
    def __init__(self, centroid):
        self.centroid = centroid
        self.docList = []
    def clear(self):
        del self.docList[:]
    def add(self, doc):
        self.docList.append(doc)

    #recompute centroid, and return the variation (distance) between the new centroid and old centroid
    def recomputeCentroid(self):
        newCentroid = {}
        n = len(self.docList) * 1.0
        for doc in self.docList:
            for token,val in doc.feaVec.iteritems():
                if newCentroid.has_key(token):
                    newCentroid[token] += val/n
                else:
                    newCentroid[token] = val/n
        distance = 1 - calSim(newCentroid, self.centroid)
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

def getInitClusters(K):
    centroidDocs = []
    for i in range(K):
        while True:
            n = random.randint(0, len(docList)-1)
            if docList[n] not in centroidDocs:
                break
        centroidDocs.append(docList[n])
    return [KmsCluster(doc.feaVec) for doc in centroidDocs]
    
# return the number of iterations executed
def kmeans(K, threshold, clusters):
    #clusters = getInitClusters(K)
    iter = 0
    while True:
        iter += 1
        for doc in docList:
            sim = -1
            cluster = None
            for c in clusters:
                newSim = calSim(doc.feaVec, c.centroid)
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
        #if iter==1:
            #break
        else:
            for c in clusters:
                c.clear()
    #return clusters
    return iter

def printClusters(clusters):
    if Verbose:
        i = 0
        for cluster in clusters:
            #print cluster.centroid
            print "cluster " + str(i) + ": " +str(len(cluster.docList))
            i += 1
    print "entropy: " + str(calEntropy(clusters))
    print "skew: " + str(calSkew(clusters))

if __name__ == '__main__':
    readVectors("../FreqVectors.txt")

    for K in numClusters:
        startTime = time.time()
        clusters = getInitClusters(K)
        iter = kmeans(K, Threshold, clusters)
        elapse = time.time() - startTime
        print "################"
        print str(K) + " clusters:"
        print "iterations: " + str(iter)
        print "time: " + str(elapse)
        printClusters(clusters)


