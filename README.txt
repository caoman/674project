Name: Man Cao, Lilong Jiang
###################################################################
Work:
The code and document is written and edited by both students.

###################################################################
How to run the program:
1. Unpack the submitted files:

	tar xzf submission.tar.gz

2. Make sure your computer is connected to the internet. It will download some nltk packages automatically at the first run. 
   In the terminal, run the following command:

	python main.py [n]

where n is an optional numeric argument that limits the maximum number of documents to be processed in each input file.

During runtime, it will print the 'NEWID' of the document processed. It will take a long time to finish processing all the files.

It is highly recommended for the grader to run the following command:

	python main.py 3

which will only process the first 3 documents in each input file, and will quickly give an idea of our workflow.

###################################################################
Directory structure:
README.txt: 		This file.
main.py:  		The source code of this project.
docs\report1.pdf:	The report for this project.
docs\report1.tex:	The LateX source for our report.
(The followings are library dependences:)
bs4: 			Beautiful Soup 4.3.1 (http://www.crummy.com/software/BeautifulSoup/)
nltk:	 		Natural Language Toolkit 2.0.4 (http://nltk.org/)
yaml:	 		PyYAML-3.10 (http://pyyaml.org/)

###################################################################
Output:
freqVectors.txt		The term frequency vector for each document.
tfidfVectors.txt 	The tf-idf vector for each document.

