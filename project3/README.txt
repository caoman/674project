Name: Man Cao, Lilong Jiang
###################################################################
Work:
The code and document is written and edited by both students.

###################################################################
How to run the program:
1. Unpack the submitted files:

	tar xzf submission.tar.gz

2. Run the following command:
   a). For Hierarchical clustering:

	python HierachCluster.py
	(Note: It will first compute result with Cosine similarity, then compute with Jaccard.)

   b). For K-means clustering:
        
	python kmeans.py
	(Note: You can comment/uncomment one of the two lines "calSim = ..." to toggle between Cosine and Jaccard similarities.) 


###################################################################
Directory structure:
README.txt: 		This file.
HierachCluster.py:  	The source code for Hierarchical clustering.
kmeans.py:		The source code for K-means clustering.
helperFunctions.py:	The source code for functions shared between both clustering algorithms.
report.pdf:		The report for this project.
FreqVectors.txt:	The input file for the source code (only 2500 documents).

###################################################################
Output:
For Hiecharchical clustering, it prints the progress of building the proximity matrix (how many documents have been processed so far),
and the progress of clustering (how many mergings of two clusters have happened). The final clustering result is written to the file
"Result.txt", which contains the computation time, skew and entropy of the clustering, as well as the IDs of the documents in each cluster.

For K-means, it prints the progress of the clustering (how many iterations have been performed), and the maximum distance between 
new centroid and old centroid among all clusters after the current iteration. The final clustering result is printed to stdout,
which contains the computation time, number of iterations, skew and entropy of the clustering.

