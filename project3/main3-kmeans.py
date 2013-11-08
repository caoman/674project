# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Nov 3, 2013

@author: man
'''
import os, math, random
from helperFunctions import *

docList = []

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
        for doc in self.docList:
            for token,val in doc.feaVec.iteritems():
                if newCentroid.has_key(token):
                    newCentroid[token] += val
                else:
                    newCentroid[token] = val
        n = len(self.docList) * 1.0
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
    iter = 0
    while True:
        iter += 1
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
        if iter==1:
            break
        else:
            for c in clusters:
                c.clear()
    return clusters

def printClusters(clusters):
    for cluster in clusters:
        #print cluster.centroid
        print len(cluster.docList)
        print "#####"

if __name__ == '__main__':
    readVectors("../FreqVectors-all.txt")
    clusters = kmeans(4, 0.3)
    printClusters(clusters)
