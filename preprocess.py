from bs4 import BeautifulSoup






def processFile(filename):
	soup = BeautifulSoup(infile)
	#outfile.print(soup.title)
	#titles = soup.find_all('title')
	entries = soup.find_all('reuters')

for t in entries:
	print t.get('newid')

