from bs4 import BeautifulSoup
from classes import *




def processFile(filename):
	infile = open(filename, 'r')
	outfile = open('out'+filename+'.txt', 'w')
	soup = BeautifulSoup(infile, "xml")
	#outfile.print(soup.title)
	#titles = soup.find_all('title')
	entries = soup.find_all('REUTERS')
	rows = []

	for e in entries:
                #print e.get_text()
		row = Row()
		row.id = e.get('NEWID')
		print row.id
		"""topics = e.find('topics')
		if (len(topics.contents)>0):
			row.topics=[topic.string for topic in topics.find_all('d')]
			#for topic in topics.find_all('d'):
			#	row.topics.append(topic.string)
		"""
		#topicText=''
		#topic = e.topics
		#if topic is not None: topicText = topic.getText()
		#print topicText
		#title = text.TITLE 
		
		rows.append(row)
		#outfile.writelines(e.get('newid'))
		#print row.topics
		#print e.topics
		#text = e.find('text')
		#print text.title
		#print text.body
		#print text.dateline

	infile.close()
	outfile.close()



processFile('reut2-000.sgm')
