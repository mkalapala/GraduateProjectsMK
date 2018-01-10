#NAME: TRAINING SVM FOR CLS SCORE PREDICTIONS
#DATE CREATED: 24/11/2014
#This module contains functions that help in  dividing of data into 2 classes,perform gridding,dividing tesing and training sets and calculation of cls scores
import csv
import numpy as np
from sklearn import svm, cross_validation, metrics, preprocessing
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report, precision_score, recall_score

# This function imports the svm ready file that is the output file containing numeric codes.
def get_fdd(filename):  # function name and filename argument
    csvfile=open(filename,  "r") # opens the file named in fname
    fdd= csv.reader(csvfile, delimiter=",") # csv.reader reads 
                                          # in a csv type file
    rows = list(fdd)      # create a list of the rows that are read in
    csvfile.close()       # close the file we don't need it anymore
    
    fdd_data=np.array([rows[0]], dtype='a70') # create a 2D array starting with first row
    for row in rows[1:]:      # create numpy array of each subsequent row 
                              # except the first row
        fdd_data = np.vstack((fdd_data, np.array(row, dtype='a20')))

    return fdd_data # return the list of rows
        
fdd = get_fdd("FDD_DATA_SET_OUT.csv")

#Header slicing
fdd_header = fdd[1:]

#index slicing
index_removed = fdd_header[ :,1:20]
# After the header and the index point is removed the output class is extracted from the dataset
# we perform grdding proccess to specify the kernels that we need to test for

#The following variables specify the kernels that we wish to test for.
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0.0, 1e-2, 1e-3, 1e-4], 'C': [1, 10, 100, 1000, 10000] }, \
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000, 10000] }, \
                    {'kernel': ['poly'], 'degree': [1, 2, 3], 'coef0': [0.0, 1., 2.], 'C': [1, 10, 100, 1000, 10000] }, \
                    {'kernel': ['sigmoid'], 'degree': [1, 2, 3],  'coef0': [0.0, 1., 2.],  'gamma': [0.0, 1e-2, 1e-3, 1e-4], 'C': [1, 10, 100, 1000, 10000]}  ]

tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0.0, 1e-2], 'C': [1, 10] },\
                    {'kernel': ['linear'], 'C': [1, 10] }]

tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0.0, 1e-2, 1e-3, 1e-4], 'C': [1, 10, 100] }]


# specifies score optimization
scores = [ ('accuracy', 'accuracy'), ('average_precision', 'average_precision'), ('recall', 'recall')]

#extracts output coloum to y variable
y= np.array(index_removed[:,14],dtype = int)
print y

i=np.delete(index_removed,14,1)
print i
#extracts rest of the dataset to variable x and gives them floating point datatype 
X=np.array(i[:,:18],dtype=float)
print X

print "Starting the gridding process."
#checks number of 0's and 1's in output class and takes the minimum as cv_size
num_class_0 = list(y).count(0)
print num_class_0
num_class_1 = list(y).count(1)
print num_class_1
cv_size = min(num_class_0, num_class_1)
print cv_size

"""Now we loop through the list of kernels and parameter setting 
to try and get as close as possible to the best setting to
use for our prediction machine. """

for score_name, score_func in scores:
    print "   Tuning SVM parameters for %s" % score_name
    print 

    clf = GridSearchCV( SVC(C=1), tuned_parameters, scoring = score_func)
    clf.fit(X, y)
    """
    """
    clf_scores = cross_validation.cross_val_score(clf, X, y, cv = cv_size)
    print
    print "CLF SCORES: ==================================="
    print  score_name, ": %0.2f (+/- %0.2f)" % (clf_scores.mean(), clf_scores.std() * 2)
    print "==============================================="
    print "Best parameters set found on development set:"
    print
    print clf.best_estimator_
    print 
    print
    

"""Dividing the data into training set and testing set, the test_size=0.2
gets 20% as testing set.Different percentages of testing sets are checked using different kernels to get the best accuracy
"""
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=0)
print "X_train shape =", X_train.shape, "  y_train shape=", y_train.shape
print "X_test shape =", X_test.shape, "  y_test shape=", y_test.shape
print


""" Trains the SVM using extracted training dataset and
is parameterized based on the gridding results. Then the trained SVM is
used to carry out predictions on the test data set. The percentage 
of accuract predictions is printed
"""
if __name__ == '__main__':
    clf = svm.SVC(kernel='rbf', C=1, gamma = 0.0, degree = 3.0, coef0 = 0.0).fit(X_train, y_train)
    print "clf.get_params(deep=True) =", clf.get_params(deep=True)
    print "clf.score(X_test, y_test) = {0}%".format(int((clf.score(X_test, y_test) * 10000))/100.)
    print
