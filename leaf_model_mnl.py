#This program is a LeafModel class for the MST package that orchestrates
#which of 2 candidate MNL fitting procedures is called to train an MNL model.
#Option 1: tensorflow-based implementation using stochastic gradient descent
#Option 2: R-based implementation using the mnlogit package
#The choice between Option 1 and Option 2 depends on the size of the training
#data (if the amount of observations > 1000000 then Option 1 is called, else 
#Option 2)
#
#Copyright (C) 2020  Ryan McNellis
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import numpy as np
from leaf_model_mnl_tensorflow import *
from leaf_model_mnl_rmnlogit import *

'''
MST depends on the classes and functions below. 
These classes/methods are used to define the leaf model object in each leaf node,
as well as helper functions for certain operations in the tree fitting procedure.

One can feel free to edit the code below to accommodate any leaf node model.
The leaf node model is fit on data (A,Y). (A is are the decisions "P" in the paper).
Make sure to add an import statement to mst.py importing this leaf model class.

Summary of methods and functions to specify:
  Methods as a part of class LeafModel: fit(), predict(), to_string(), error(), error_pruning()
  Other helper functions: get_sub(), are_Ys_diverse()
  
'''

'''
LeafModel: the model used in each leaf. 
Has five methods: fit, predict, to_string, error, error_pruning
'''
class LeafModel(object):
  
  #Any additional args passed to MST's init() function are directly passed here
  def __init__(self,*args,**kwargs):
    self.mnl = None
    return
  
  '''
  This function trains the leaf model on the data (A,Y,weights).
  
  A and Y can take any form (lists, matrices, vectors, etc.). For our applications, I recommend making Y
  the response data (e.g., choices) and A alternative-specific data (e.g., prices, choice sets)
  
  weights: a numpy array of case weights. Is 1-dimensional, with weights[i] yielding 
    weight of observation/customer i. If you know you will not be using case weights
    in your particular application, you can ignore this input entirely.
  
  refit: boolean which equals True iff leaf model is being refit after tree splits have been decided. Since
      the tree split evaluation process requires fitting a large number of leaf models, one might wish to 
      fit the leaf models on only a subset of data or for less training iterations when refit=False. Practitioners
      can feel free to ignore this parameter in their leaf model design.
  
  Returns 0 or 1.
    0: No errors occurred when fitting leaf node model
    1: An error occurred when fitting the leaf node model (probably due to insufficient data)
  If fit returns 1, then the tree will not consider the split that led to this leaf node model
  
  fit_init is a LeafModel object which represents a previously-trained leaf node model.
  If specified, fit_init is used for initialization when training this current LeafModel object.
  Useful for faster computation when fit_init's coefficients are close to the optimal solution of the new data.
  
  For those interested in defining their own leaf node functions:
    (1) It is not required to use the fit_init argument in your code
    (2) All edge cases must be handled in code below (ex: arguments
        consist of a single entry, weights are all zero, Y has one unique choice, etc.).
        In these cases, either hard-code a model that works with these edge-cases (e.g., 
        if all Ys = 1, predict 1 with probability one), or have the fit function return 1 (error)
    (3) Store the fitted model (or its coefficients) as an attribute to the self object. You can name the attribute
        anything you want (i.e., it does not have to be self.model_obj below),
        as long as its consistent with your predict_prob() and to_string() methods
  
  Any additional args passed to MST's fit() function are directly passed here
  '''
  def fit(self, A, Y, weights, fit_init=None, leaf_mod_thresh=1000000, **kwargs):
    
    '''
    There are two different implementations of fitting vanilla MNL models that are considered:
      - "tensorflow": custom implementation of stochastic gradient descent with minibatching using tensorflow
      - "rmnlogit": calls the R mnlogit package to fit the MNL model using Newton's method 
                    (significantly faster for smaller and medium-sized data)
    If the number of training observations in this leaf node <= leaf_mod_thresh, then the rmnlogit
    implementation is applied. Otherwise, the tensorflow implementation is applied.
    
    If fit_init is provided, we warm-start the current leaf model fit with the coefficients from fit_init IF
    fit_init was trained using the same algorithm (tensorflow vs rmnlogit) as the current model under consideration.
    '''
    
    if (len(Y) > leaf_mod_thresh):
      self.leaf_mod_type = "tensorflow"
      if fit_init is not None and fit_init.leaf_mod_type == "tensorflow":
        fit_init = fit_init.mnl
      else:
        fit_init = None
      
      if self.mnl is None:
        self.mnl = LeafModelTensorflow()
    
    else:
      self.leaf_mod_type = "rmnlogit"
      if fit_init is not None and fit_init.leaf_mod_type == "rmnlogit":
        fit_init = fit_init.mnl
      else:
        fit_init = None
      
      if self.mnl is None:
        self.mnl = LeafModelRMNLogit()
    
    error = self.mnl.fit(A, Y, weights, fit_init=fit_init, **kwargs)
    return(error)
    
  '''
  This function applies model from fit() to predict response data given new data A.
  Returns a numpy vector/matrix of response probabilities (one list entry per observation, i.e. l[i] yields prediction for ith obs.).
  Note: make sure to call fit() first before this method.
  
  Any additional args passed to MST's predict() function are directly passed here
  '''
  def predict(self, *args,**kwargs):
    return(self.mnl.predict(*args,**kwargs))
    
  
  '''
  This function outputs the errors for each observation in pair (A,Y).  
  Used in training when comparing different tree splits.
  Ex: log-likelihood between observed data Y and predict(A)
  Any error metric can be used, so long as:
    (1) lower error = "better" fit
    (2) error >= 0, where error = 0 means no error
    (3) error of fit on a group of data points = sum(errors of each data point)
  
  How to pass additional arguments to this function: simply pass these arguments to the init()/fit() functions and store them
  in the self object.
  '''
  def error(self,A,Y):
    return(self.mnl.error(A,Y))
  
  '''
  This function outputs the errors for each observation in pair (A,Y).  
  Used in pruning to determine the best tree subset.
  Ex: mean-squared-error between observed data Y and predict(A)
  Any error metric can be used, so long as:
    (1) lower error = "better" fit
    (2) error >= 0, where error = 0 means no error
    (3) error of fit on a group of data points = sum(errors of each data point)
  
  How to pass additional arguments to this function: simply pass these arguments to the init()/fit() functions and store them
  in the self object.
  '''
  def error_pruning(self,A,Y):
    return(self.mnl.error_pruning(A,Y))
  
  '''
  This function returns the string representation of the fitted model
  Used in traverse() method, which traverses the tree and prints out all terminal node models
  
  Any additional args passed to MST's traverse() function are directly passed here
  '''
  def to_string(self,*leafargs,**leafkwargs):
    return(self.mnl.to_string(*leafargs,**leafkwargs))
    

'''
Given decision vars A, response data Y, and observation indices data_inds,
extract those observations of A and Y corresponding to data_inds

If only decision vars A is given, returns A.
If only response data Y is given, returns Y.

If is_boolvec=True, data_inds takes the form of a boolean vector which indicates
the elements we wish to extract. Otherwise, data_inds takes the form of the indices
themselves (i.e., ints).

Used to partition the data in the tree-fitting procedure
'''
def get_sub(data_inds,A=None,Y=None,is_boolvec=False):
  if A is None:
    return Y[data_inds]
  if Y is None:
    return A[data_inds]
  else:
    return A[data_inds],Y[data_inds]  

'''
This function takes as input response data Y and outputs a boolean corresponding
to whether all of the responses in Y are the same. 

It is used as a test for whether we should make a node a leaf. If are_Ys_diverse(Y)=False,
then the node will become a leaf. Otherwise, if the node passes the other tests (doesn't exceed
max depth, etc), we will consider splitting on the node. If you do not want to specify any
termination criterion, simply "return True"
'''
def are_Ys_diverse(Y):
  return (len(np.unique(Y)) > 1)

