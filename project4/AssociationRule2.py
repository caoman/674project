# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
'''
Created on Nov 17, 2013

@author: lilong, man
'''
import Orange, os
import AssociationRule1, Kmeans
from AssociationRule1 import *
from Kmeans import *

DOMAIN = None
Verbose = True
AssociationRule1.Verbose, Kmeans.Verbose = Verbose, Verbose

class ClusterWithRules:
    def __init__(self, cluster):
        self.centroid = cluster.centroid
        data = Orange.data.Table(DOMAIN)
        topicCnt = {}
        for doc in cluster.docList:
            vec = doc.feaVec.keys() + [topic.upper() for topic in doc.topics]
            inst = Orange.data.Instance(DOMAIN)
            for word in vec:
                inst[word]=1.0
            data.append(inst)
            for topic in doc.topics:
                if topic in topicCnt.keys():
                    topicCnt[topic] += 1
                else:
                    topicCnt[topic] = 1
        rules = Orange.associate.AssociationRulesSparseInducer(data, support = 0.1, store_examples = True)
        self.rules = prune(rules)
        if Verbose:
            Orange.associate.print_rules(self.rules, ["support", "confidence", "lift"])
        print "rules in cluster: " + str(len(self.rules))
        self.defaultTopic = max(topicCnt, key=topicCnt.get)

def testWithClusterForInstance(ruleClusters, doc):
    maxSim = -1
    targetCluster = None
    for c in ruleClusters:
        sim = calSim(doc.feaVec, c.centroid)
        if sim > maxSim:
            maxSim = sim
            targetCluster = c
    return TestRuleForInstance(doc, targetCluster.rules, targetCluster.defaultTopic)

def CBAwithCluster(numCluster, data):
    clusters = runKmeans(numCluster, Threshold)
    #if Verbose:
    printClusters(clusters)
    ruleClusters = [ClusterWithRules(cluster) for cluster in clusters]
    accurateCnt = 0
    for doc in docList:
        accurateCnt += testWithClusterForInstance(ruleClusters, doc)
    accuracy = accurateCnt * 1.0 / len(docList)
    print "Accuracy:" + str(accuracy)

if __name__ == '__main__':
    readVectors(freqFileName)
    if not os.path.isfile(transFileName):
        transformVec()
    data = Orange.data.Table(transFileName)
    DOMAIN = data.domain
    for numCluster in numClusters:
        CBAwithCluster(numCluster, data)
        
