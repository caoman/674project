# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
Created on Nov 3, 2013

@author: lilong, man
'''
import math

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

def calJaccard(vec1, vec2):
#    print vec1
#    print vec2
    numerator = 0
    denominator = 0
    
    for token, val in vec1.iteritems():
        denominator += val * val
        if vec2.has_key(token):
            numerator += val * vec2[token]
#    print "denom1:" + str(denominator)
    for val in vec2.itervalues():
        denominator += val * val
    
    denominator -= numerator
#    print "num:" + str(numerator) + " denominator:" + str(denominator)
    if denominator == 0: return 0    
    return (numerator * 1.0 / denominator)

#calculate the variance the cardinalities of the clusters
def calSkew(clusters):
    clusterCards = []
    clusterCnt = len(clusters)
    sumCard = 0
    avgCard = 0
    var = 0
    
    for cluster in clusters:
        curCard = len(cluster.docList)
        clusterCards.append(curCard)
        sumCard += curCard
    avgCard = sumCard * 1.0 / len(clusters)
    
    for clusterCard in clusterCards:
        var += (clusterCard - avgCard) * (clusterCard - avgCard)
    var = var / clusterCnt
    return var 

def calEntropy(clusters):
    totalEntropy = 0
    totalCnt = 0
    
    for cluster in clusters:
        curEntropy = 0
        topicDict = {}
        docCnt = 0          #the doc with multiple topics is counted as multiple times
        for doc in cluster.docList:
            for topic in doc.topics: 
                docCnt += 1
                if topicDict.has_key(topic):
                    topicDict[topic] += 1
                else:
                    topicDict[topic] = 1
        for topic, cnt in topicDict.items():
            percent = float(cnt) / docCnt
            curEntropy -= percent * math.log(percent, 2)
        totalEntropy += curEntropy * docCnt
        totalCnt += docCnt
    totalEntropy /= totalCnt
    return totalEntropy

