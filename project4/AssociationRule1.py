# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
'''
Created on Nov 17, 2013

@author: lilong, man
'''
import Orange

transFileName = "Transactions.basket"
freqFileName = "FreqVectors.txt"
valFold = 5
assRules = []
Verbose = True 
K = 5      #How many rule selected for testing the instance
#ordering =["confidence", "support"] 
#ordering =["support","confidence"] 
ordering =["lift", "support", "confidence"] 
#ordering =["n_left","lift","support","confidence"]

#Transform vector from the key-value to transaction form
def transformVec():
    global topicSet
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

def pruneByLhsRhs(rules):
    print "pruning by LHS and RHS of rules ..."
    savedRules = []
    for rule in rules:
        rightList = [value.variable.name for value in rule.right.get_metas().values()]
        #print rightList
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
    print "sorting rules ..."
    Orange.associate.sort(rules, ordering)
    print "pruning by subsumption ..."
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

def TestRuleForInstance(testInstance):
    words = set([value.variable.name for value in testInstance.get_metas().values() if value.variable.name.islower()])
    topics = set([value.variable.name for value in testInstance.get_metas().values() if value.variable.name.isupper()])
    #print "docWords:" + str(words)
    #print "docTopics:" + str(topics)
    
    ruleCnt = 0
    preTopics = set()
    for rule in assRules:
        ruleWords = set([value.variable.name for value in rule.left.get_metas().values()])
        ruleTopics = set([value.variable.name for value in rule.right.get_metas().values()])
        #print "RuleWord:" + str(ruleWords)
        #print "RuleTopics:" + str(ruleTopics)
        if ruleWords.issubset(words) and ruleCnt < K:
            preTopics = preTopics.union(ruleTopics)
            ruleCnt += 1
    #print "RuleTopics:" + str(preTopics)
    if topics.issubset(preTopics):
        return True
    else:
        return False      
    
def getAssociationRules():
    global assRules
    data = Orange.data.Table(transFileName)

    #Cross Validation
    cvIndices = Orange.data.sample.SubsetIndicesCV(data, valFold)
    accuracy = 0
    for fold in range(valFold):
        train = data.select(cvIndices, fold, negate = 1)
        test  = data.select(cvIndices, fold)
        totalTestCnt = len(test)
        accurateCnt = 0
                
        rules = Orange.associate.AssociationRulesSparseInducer(train, support = 0.02, store_examples = True)
        rules = pruneByLhsRhs(rules)
        assRules = pruneBySubsumption(rules)
        if Verbose:
            Orange.associate.print_rules(assRules, ["support", "confidence", "lift"])
        print "total # of rules: " + str(len(assRules))
        for testInstance in test:
            if TestRuleForInstance(testInstance) is True:
                accurateCnt += 1
        accuracy += accurateCnt * 1.0 / totalTestCnt
        break
    print "Accuracy:" + str(accuracy)

if __name__ == '__main__':
    #transformVec()
    getAssociationRules()
    
