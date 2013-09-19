'''
Created on Sep 18, 2013

@author: lilong
'''
import re, os

docList = []

class Doc:
    def __init__(self, topics, feaVec):
        self.topics = topics
        self.feaVec = feaVec

class KNNTopicClass:
    def __init__(self):
        self.centroidVec = {}
        self.docCnt = 0
        
    def updateCentVec(self, doc):
        self.docCnt += 1
        
        for token, val in doc.feaVec:
            if self.tokenDict.has_key(token):  self.centroidVec[token] += val
            else: self.centroidVec[token] = 1
    
    def setCentroid(self):
        for token, val in self.centroidVec:
            self.centroidVec[token] = float(val) / self.docCnt 

def readVectors(fileName):
    global docList
    vecFile = open(fileName, 'r')
    
    while True:
        metaData = vecFile.readline() 
        if len(metaData) == 0: break
        topics = re.search('(?<=TOPICS:)[^\s]+', metaData).group(0).split(';')
        tokens = eval(vecFile.readline())     
        doc = Doc(topics, tokens)
        docList.append(doc)
        
if __name__ == '__main__':
    readVectors("1.txt")