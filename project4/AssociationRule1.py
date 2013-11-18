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
    Orange.associate.sort(rules, ["confidence", "support"])
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

def getAssociationRules():
    global assRules
    data = Orange.data.Table(transFileName)

    #Cross Validation
    cvIndices = Orange.data.sample.SubsetIndicesCV(data, valFold)
    for fold in range(valFold):
        train = data.select(cvIndices, fold, negate = 1)
        test  = data.select(cvIndices, fold)
        rules = Orange.associate.AssociationRulesSparseInducer(train, support = 0.1, store_examples = True)
        rules = pruneByLhsRhs(rules)
        rules = pruneBySubsumption(rules)
        if Verbose:
            Orange.associate.print_rules(rules, ["support", "confidence"])
        print "total # of rules: " + str(len(rules))
        break


if __name__ == '__main__':
    #transformVec()
    getAssociationRules()
    
