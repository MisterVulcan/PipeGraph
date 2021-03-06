"""
.. _example4:

Fourth Example: Combination of classifiers
-------------------------------------------------

A set of classifiers is combined as input to a neural network. Additionally, the scaled inputs are injected as well to
the neural network. The data is firstly transformed by scaling its features.

Steps of the **PipeGraph**:

- **scaler**: A :class:`MinMaxScaler` data preprocessor
- **gaussian_nb**: A :class:`GaussianNB` classifier
- **svc**: A :class:`SVC` classifier
- **concat**: A :class:`Concatenator` custom class that appends the outputs of the :class:`GaussianNB`, :class:`SVC` classifiers, and the scaled inputs.
- **mlp**: A :class:`MLPClassifier` object

.. figure:: https://raw.githubusercontent.com/mcasl/PipeGraph/master/examples/images/Diapositiva4.png

    Figure 1. PipeGraph diagram showing the steps and their connections
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from pipegraph.base import PipeGraph, Concatenator
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

iris = load_iris()
X = iris.data
y = iris.target

scaler = MinMaxScaler()
gaussian_nb = GaussianNB()
svc = SVC()
mlp = MLPClassifier()
concatenator = Concatenator()

steps = [('scaler', scaler),
         ('gaussian_nb', gaussian_nb),
         ('svc', svc),
         ('concat', concatenator),
         ('mlp', mlp)]


###############################################################################
# In this example we use a :class:`PipeGraphClassifier` because the result is a classification and we want to take advantage of Scikit-Learn default scoring method for classifiers.

pgraph = PipeGraph(steps=steps)
(pgraph.inject(sink='scaler', sink_var='X', source='_External', source_var='X')
       .inject('gaussian_nb', 'X', 'scaler')
       .inject('gaussian_nb', 'y', source_var='y')
       .inject('svc', 'X', 'scaler')
       .inject('svc', 'y', source_var='y')
       .inject('concat', 'X1', 'scaler')
       .inject('concat', 'X2', 'gaussian_nb')
       .inject('concat', 'X3', 'svc')
       .inject('mlp', 'X', 'concat')
       .inject('mlp', 'y', source_var='y')
)

param_grid = {'svc__C': [0.1, 0.5, 1.0],
              'mlp__hidden_layer_sizes': [(3,), (6,), (9,),],
              'mlp__max_iter': [5000, 10000]}

grid_search_classifier  = GridSearchCV(estimator=pgraph, param_grid=param_grid, refit=True)
grid_search_classifier.fit(X, y)
y_pred = grid_search_classifier.predict(X)

grid_search_classifier.best_estimator_.get_params()


# Code for plotting the confusion matrix taken
#  from 'Python Data Science Handbook' by Jake VanderPlas
from sklearn.metrics import confusion_matrix
import seaborn as sns; sns.set()  # for plot styling

mat = confusion_matrix(y_pred, y)
sns.heatmap(mat.T, square=True, annot=True, fmt='d', cbar=False)
plt.xlabel('true label')
plt.ylabel('predicted label');

plt.show()


###############################################################################
# This example displayed complex data injections that are successfully managed by **PipeGraph**.
# Next example :ref:`on <example5>`.
