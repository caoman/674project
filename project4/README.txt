Name: Man Cao, Lilong Jiang
###################################################################
Work:
The code and document are written and edited by both students.

###################################################################
How to run the program:
1. Unpack the submitted files:

        tar xzf submission.tar.gz

2. Run the following command:
   a). For Algorithm 1:

        python AssociationRule1.py

   b). For Algorithm 2:
        
        python AssociationRule2.py


###################################################################
Directory structure:
README.txt:                  This file.
AssociationRule1.py:         The source code for Algorithm 1.
AssociationRule2.py:         The source code for Algorithm 2.
Kmeans.py:                   The source code for K-means clustering.
helperFunctions.py:          The source code for functions shared by other files.
report.pdf:                  The report for this project.
FreqVectors.txt:             The input file for the source code.
###################################################################
Output:
'Verbose' parameter in the source code is used to determine whether to print the rules or not.

For Algorithm 1, it prints the minimum support, the rules subsumed, the final rules(when Verbose = TRUE), K value, time for building the model, time for testing the model, accuracy, precision, recall and F-measure.

For Algorithm 2, it prints the progress of the K-means clustering (how many iterations have been performed), the maximum distance between 
new centroid and old centroid among all clusters after the current iteration, the number of clusters, clustering time, minimum support, the rules subsumed, the final rules(when Verbose = TRUE), rule construction time, test time, accuracy, precision, recall and F-measure. 
