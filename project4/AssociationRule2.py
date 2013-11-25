# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
'''
Created on Nov 17, 2013

@author: lilong, man
'''
import Orange, os, time
import AssociationRule1, Kmeans
from AssociationRule1 import *
from Kmeans import *

DOMAIN = None
Verbose = False
AssociationRule1.Verbose, Kmeans.Verbose = Verbose, Verbose
Kmeans.Verbose = True
testDocList = []

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
        self.defaultTopic = max(topicCnt, key=topicCnt.get).upper()
        #print self.defaultTopic
    
    def updateRules(self, minSup):
        rules = Orange.associate.AssociationRulesSparseInducer(data, support = minSup, store_examples = True)
        self.rules = prune(rules)
        #print "rules in cluster: " + str(len(self.rules))
        if Verbose:
            Orange.associate.print_rules(self.rules, ["support", "confidence", "lift"])

def testWithClusterForInstance(ruleClusters, doc, instanceIndex, K, preTopicVecDict, testTopicVecDict):
    maxSim = -1
    targetCluster = None
    for c in ruleClusters:
        sim = calSim(doc.feaVec, c.centroid)
        if sim > maxSim:
            maxSim = sim
            targetCluster = c
    return TestRuleForInstance(doc, targetCluster.rules, targetCluster.defaultTopic, instanceIndex, K, preTopicVecDict, testTopicVecDict)


def CBAwithCluster(numCluster):

    print "####################################"
    print "number of clusters: " +  str(numCluster)
    startTime = time.time()
    clusters = runKmeans(numCluster, Threshold)
    #printClusters(clusters)
    ruleClusters = [ClusterWithRules(cluster) for cluster in clusters]
    clustering_time = time.time() - startTime
    print "Clustering time: " + str(clustering_time)
    for minSup in MIN_SUPs:
        print
        print "MinSupport = " + str(minSup)
        startTime = time.time()
        for ruleCluster in ruleClusters:
            ruleCluster.updateRules(minSup)
        rule_time = time.time() - startTime
        print "Rule construction time: " + str(rule_time)
        for K in Ks:
            print "top-K rules, K= " + str(K)
            preTopicVecDict = {}
            testTopicVecDict = {}
            accurateCnt = 0
            instanceIndex = 0
            startTime = time.time()
            for doc in testDocList:
                instanceIndex += 1
                accurateCnt += testWithClusterForInstance(ruleClusters, doc, instanceIndex, K, preTopicVecDict, testTopicVecDict)
            test_time = time.time() - startTime
            print "Test time: " + str(test_time)
            print "Average test time for one doc: " + str(test_time/len(testDocList))
            accuracy = accurateCnt * 1.0 / len(testDocList)
            print "Accuracy: " + str(accuracy)
            computePrecisionRecall(preTopicVecDict, testTopicVecDict)

if __name__ == '__main__':
    readVectors(freqFileName)
    testDocList = Kmeans.docList[len(Kmeans.docList)*4/5 : ]
    Kmeans.docList = Kmeans.docList[0 : len(Kmeans.docList)*4/5]

    if not os.path.isfile(transFileName):
        transformVec()
    data = Orange.data.Table(transFileName)
    DOMAIN = data.domain
    for numCluster in numClusters:
        CBAwithCluster(numCluster)
        
