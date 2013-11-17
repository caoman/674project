'''
Created on Nov 17, 2013

@author: lilong
'''
import Orange

transFileName = "Transactions.basket"
freqFileName = "FreqVectors.txt"
valFold = 5
assRules = []

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

def getAssociationRules():
    global assRules
    data = Orange.data.Table(transFileName)

    #Cross Validation
    cvIndices = Orange.data.sample.SubsetIndicesCV(data, valFold)
    for fold in range(valFold):
        train = data.select(cvIndices, fold, negate = 1)
        test  = data.select(cvIndices, fold)
        rules = Orange.associate.AssociationRulesSparseInducer(train, support = 0.3)   
        
        for rule in rules:
            rightList = [value.variable.name for value in rule.right.get_metas().values()]
            #print rightList
            topicFlag = True
            for rightElem in rightList:
                if rightElem.islower():
                    topicFlag = False
            if topicFlag is True:
                assRules.append(rule)

if __name__ == '__main__':
    #transformVec()
    getAssociationRules()
    