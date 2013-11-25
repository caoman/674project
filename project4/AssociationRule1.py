# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
'''
Created on Nov 17, 2013

@author: lilong, man
'''
import Orange, math, time


transFileName = "Transactions.basket"
freqFileName = "FreqVectors.txt"
valFold = 5
Verbose = False 
MIN_SUPs = [0.05, 0.1, 0.15]
Ks = [1,2,3,4,5]   #How many rule selected for testing the instance
DEFAULT_TOPIC = ""
ordering =["lift", "confidence", "support"]     #order by lift firstly, then by confidence, and then by support


#Transform vector from key-value to transaction form
def transformVec():
    freqFile = open(freqFileName, 'r')
    transFile = open(transFileName, 'w')

    while True:
        metaData = freqFile.readline() 
        if len(metaData) == 0: break
        metaVec = eval(metaData)
        freqVec = eval(freqFile.readline())    
        transFile.write(",".join(freqVec.keys() + [topic.upper() for topic in metaVec["TOPICS"]]) + "\n")
    freqFile.close()
    transFile.close()        

#prune the rule which the left side or right side contains the topics
def pruneByLhsRhs(rules):
    #print "pruning by LHS and RHS of rules ..."
    savedRules = []
    for rule in rules:
        rightList = [value.variable.name for value in rule.right.get_metas().values()]
        topicFlag = True
        for rightElem in rightList:
            if rightElem.islower():
                topicFlag = False
    	        break
    	if topicFlag:
            leftList = [value.variable.name for value in rule.left.get_metas().values()]
            for leftElem in leftList:
                if leftElem.isupper():
                    topicFlag = False
                    break
        if topicFlag:
            savedRules.append(rule)
    return savedRules

def pruneBySubsumption(rules):
    #print "sorting rules ..."
    Orange.associate.sort(rules, ordering)
    #print "pruning by subsumption ..."
    savedRules = []
    subsumedRules = []
    # a topic is just an int index in data.domain
    dictTopicRules = {} # mapping of a topic to rules that can predict this topic
    for rule in rules:
        subsumed = False
        for topic in rule.right.get_metas().keys():
            if topic in dictTopicRules:
                knownRules = dictTopicRules[topic]
                for kr in knownRules:
                    if set(rule.right.get_metas().keys()) <= set(kr.right.get_metas().keys()) \
                            and set(rule.match_both) <= set(kr.match_both):
                        subsumed = True
                        break
            else:
                break
            if subsumed:
                break
        if not subsumed:
            savedRules.append(rule)
            for topic in rule.right.get_metas().keys():
                if topic in dictTopicRules:
                    dictTopicRules[topic].append(rule)
                else:
                    dictTopicRules[topic]=[rule]
        else:
            subsumedRules.append(rule)
    if Verbose:
        print "# of rules subsumed: " + str(len(rules) - len(savedRules))
        print "rules subsumed: "
        Orange.associate.print_rules(subsumedRules, ["support", "confidence"])
    return savedRules

def prune(rules):
    rules = pruneByLhsRhs(rules)
    rules = pruneBySubsumption(rules)
    return rules

def TestRuleForInstance(testInstance, assRules, defaultTopic, testIndex, K, preTopicVecDict, testTopicVecDict):
    
    if isinstance(testInstance, Orange.data.Instance):
        words = set([value.variable.name for value in testInstance.get_metas().values() if value.variable.name.islower()])
        topics = set([value.variable.name for value in testInstance.get_metas().values() if value.variable.name.isupper()])
    else:
        words = set(testInstance.feaVec.keys())
        topics = set([topic.upper() for topic in testInstance.topics])

    for topic in topics:
        if testTopicVecDict.has_key(topic):
            testTopicVecDict[topic].add(testIndex)
        else:
            testTopicVecDict[topic] = set()
            testTopicVecDict[topic].add(testIndex)
    
    ruleCnt = 0
    preTopics = set()
    for rule in assRules:
        ruleWords = set([value.variable.name for value in rule.left.get_metas().values()])
        ruleTopics = set([value.variable.name for value in rule.right.get_metas().values()])
        #print "RuleWord:" + str(ruleWords)
        #print "RuleTopics:" + str(ruleTopics)
        if ruleWords.issubset(words):
            preTopics = preTopics.union(ruleTopics)
            ruleCnt += 1
        if ruleCnt > K:
            break
    if len(preTopics) == 0: 
        preTopics.add(defaultTopic)

    for topic in preTopics:
        if topic in preTopicVecDict.keys():
            preTopicVecDict[topic].add(testIndex)
        else:
            preTopicVecDict[topic] = set()
            preTopicVecDict[topic].add(testIndex)
    curAcc = len(preTopics.intersection(topics)) * 1.0 / len(topics)
    return curAcc

def splitTrain(train):
    topicVecDict = {}
    global DEFAULT_TOPIC
    
    for trainInstance in train:
        for val in trainInstance.get_metas().values():
            word = val.variable.name
            if word.isupper():
                if word in topicVecDict:
                    topicVecDict[word].append(trainInstance)
                else:
                    topicVecDict[word] = [trainInstance]
    DEFAULT_TOPIC = max(topicVecDict.keys(), key = lambda key: len(topicVecDict[key]))
    
    dataSize = len(train)
    maxTopic = ""
    for topic in topicVecDict.keys():
        if len(topicVecDict[topic]) * 1.0 / dataSize > 0.3:
            maxTopic = topic
            break
    print maxTopic
    trainList = []
    if len(maxTopic) > 0: 
        train1 = topicVecDict[maxTopic]
        train2 = [trainInstance for topic in topicVecDict.keys() if topic != maxTopic for trainInstance in topicVecDict[topic]]
        trainList = [train1, train2]
    else:
        trainList = [train]
    return trainList
    
#when combining the rules together, we need to update the suppport, confidence and lift for the rule
def update(rules1, train2):
    trainSize = rules1[0].n_examples + len(train2)
    
    for rule1 in rules1:
        rule1.support = rule1.n_applies_both / trainSize
        nLeft = rule1.n_applies_left
        nRight = rule1.n_applies_right
        for trainInstance in train2:
            if rule1.applies_left(trainInstance):
                nLeft += 1
            if rule1.applies_right(trainInstance):
                nRight += 1
        rule1.confidence = rule1.n_applies_both / nLeft
        rule1.lift = trainSize * rule1.n_applies_both / (nLeft * nRight)           
    
def getAssociationRules():
    data = Orange.data.Table(transFileName)
    
    midIndex = int(len(data) * 0.8)
    train = data[0: midIndex]
    trainList = splitTrain(train)
    test = data[midIndex + 1:]
    totalTestCnt = len(test)
    for minSup in MIN_SUPs:

        rules = []
        ruleList = []
        print "MinSupport = " + str(minSup)
        startTime = time.time()
        for train in trainList:
            tmpRules = Orange.associate.AssociationRulesSparseInducer(train, support = minSup, store_examples = True)
            tmpRules = pruneByLhsRhs(tmpRules)
            ruleList.append(tmpRules)
        if len(ruleList) > 0: 
            update(ruleList[0], trainList[1])
            update(ruleList[1], trainList[0])   
        rules = [rule for rules in ruleList for rule in rules]     
        rules = prune(rules)
        endTime = time.time()
        print "Time for building the model:" + str(endTime - startTime)
        
        if Verbose:
            Orange.associate.print_rules(rules, ["support", "confidence", "lift"])
        print "total # of rules: " + str(len(rules))
        for K in Ks:
            print "top-K rules, K= " + str(K)
            accurateCnt = 0
            accuracy = 0
            instanceIndex = 0
            preTopicVecDict = {}
            testTopicVecDict = {}
            startTime = time.time()
            for testInstance in test:
                instanceIndex += 1
                accurateCnt += TestRuleForInstance(testInstance, rules, DEFAULT_TOPIC, instanceIndex, K, preTopicVecDict, testTopicVecDict)
            endTime = time.time()
            print "Time for testing the model:" + str(endTime - startTime)
            print "Time for testing one doc:" + str((endTime - startTime) * 1.0 / len(test)) 
            accuracy += accurateCnt * 1.0 / totalTestCnt        
            print "Accuracy:" + str(accuracy)
            computePrecisionRecall(preTopicVecDict, testTopicVecDict)
    
def computePrecisionRecall(preTopicVecDict, testTopicVecDict):
    precisionList = []
    recallList = []
    fmeasureList = []
    for topic in preTopicVecDict.keys():
        interset = testTopicVecDict[topic].intersection(preTopicVecDict[topic])
        precision = len(interset) * 1.0 / len(preTopicVecDict[topic])
        recall = len(interset) * 1.0 / len(testTopicVecDict[topic])
        precisionList.append(precision)
        recallList.append(recall)
        fmeasureList.append(2 * precision * recall / (precision + recall))
    print "Precision:" + str(sum(precisionList) / len(precisionList))
    print "Recall:" + str(sum(recallList) / len(recallList))
    print "F-measure:" + str(sum(fmeasureList) / len(fmeasureList))

if __name__ == '__main__':
    transformVec()
    getAssociationRules()
    
