from DatasetReader import DatasetReader
from edf import *
from FreemanEncoder import *
import numpy as np
#from sklearn import metrics
from sklearn.cross_validation import train_test_split
#from sklearn import datasets, neighbors, linear_model
from sklearn import cross_validation
#import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
import random
from ml_base_class import ml_alg_base
from sklearn.externals import joblib
import pickle

class SVM_SVC(ml_alg_base):
    def __init__(self, num_fourier_des = 10):
        ml_alg_base.__init__(self)
        # self.reader = DatasetReader()
        self.num_fourier_des = num_fourier_des
        """        
        The following classifier configurations has been selected by the grid search
        These were the results of running the grid search for 5 times
        {'kernel': 'rbf', 'C': 100, 'degree': 2}
        0.955
        {'kernel': 'linear', 'C': 10, 'degree': 2}
        0.97
        {'kernel': 'linear', 'C': 10, 'degree': 2}
        0.98
        {'kernel': 'linear', 'C': 50, 'degree': 2}
        0.97
        {'kernel': 'linear', 'C': 10, 'degree': 2}
        0.96
        {'kernel': 'linear', 'C': 50, 'degree': 2}
        0.98
        {'kernel': 'linear', 'C': 10, 'degree': 2}
        0.965
        {'kernel': 'linear', 'C': 50, 'degree': 2}
        0.97
        {'kernel': 'linear', 'C': 50, 'degree': 2}
        0.955
        {'kernel': 'linear', 'C': 10, 'degree': 2}
        0.97

        """
        self.learning_model = svm.SVC(C=10, kernel='linear')
    
    def get_data(self, dataset_path = "./teams_dataset"):
        data_dict = self.reader.read_dataset_images(dataset_path)
        
        _,data_set_x, data_set_y = self.reader.gen_labelled_arrays(data_dict)
        data_set_y = map(int,data_set_y) #convert the string label into a number - may create a problem later!!
        data_set_x, data_set_y = self.shuffle_data(data_set_x, data_set_y)
        
        training_data = []
        for image_array in data_set_x:
            fourier_desc = self.get_fourier_desc(image_array)
            training_data.append(np.reshape(fourier_desc, (1,-1))[0])        
        
        return training_data, data_set_y
    
    def training(self, dataset_path = "./teams_dataset"):
        training_data, data_set_y = self.get_data(dataset_path)
            
        self.learning_model.fit(training_data, data_set_y)
        
        # dump the saved model in pickle file
        pickle.dump( self.learning_model, open( "./Models/svm.p", "wb" ) )
        
    def predict(self, image):
        try:
            self.learning_model = pickle.load( open( "./Models/svm.p", "rb" ) )
        except:
            print "Please train the svm model first"
            #exit()
        fourier_desc = self.get_fourier_desc(image)
        test_data = np.reshape(fourier_desc, (1,-1))[0]
        predictions = self.learning_model.predict(test_data)
        return map(str, predictions) # I return str, since I am not sure ADEL is working with integers
    
    def get_fourier_desc(self, image_array):
        efds1, K1, T1 = elliptic_fourier_descriptors(image_array,self.num_fourier_des)
        return efds1[0]
        
    def grid_search(self):
        data_x, data_y = self.get_data()
        training_data = []
        for image_array in data_x:
            fourier_desc = self.get_fourier_desc(image_array)
            training_data.append(np.reshape(fourier_desc, (1,-1))[0])
        X_train, X_test, y_train, y_test = train_test_split(training_data, data_y, test_size=0.2, random_state=0)
        tuned_parameters = {'C':[1,10,50,100],
                            'kernel':['rbf','linear','poly'],
                            'degree':[2,3,4],
                            'gamma':[10**-3,10**-2,10**-1,1,10**1,10**2]}
#        tuned_parameters = {'n_estimators':[10,20],
#                            'criterion':['gini', 'entropy'],
#                            'max_depth':[5,10]}
#        clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=5)
        clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=3)
        clf.fit(X_train, y_train)
        
        print clf.best_params_
        print clf.best_score_
        
# The grid search code - to find the best parameters
#classifier = SVM_SVC()
#for i in range(10): # I want to make sure that the estimated parameters are stable!
#    classifier.grid_search()
#classifier = SVM_SVC()
#data_x, data_y = classifier.get_data()
#classifier.first_exp(data_x, data_y, classifier.learning_model, num_iter=50, algorithm_name="svm") #change 10 later to 50