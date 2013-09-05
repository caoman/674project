from bs4 import BeautifulSoup





def processFile(filename):
	infile = open(filename, 'r')
	outfile = open('out'+filename+'.txt', 'w')
	soup = BeautifulSoup(infile)
	#outfile.print(soup.title)
	#titles = soup.find_all('title')
	entries = soup.find_all('reuters')

	for t in entries:
		outfile.writelines(t.get('newid'))

	infile.close()
	outfile.close()



processFile('reut2-000.sgm')
