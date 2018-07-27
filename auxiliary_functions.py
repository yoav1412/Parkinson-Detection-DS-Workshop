from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
from sklearn.svm import SVC, NuSVC

from constants import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
from sklearn.model_selection import cross_validate, cross_val_score, train_test_split, KFold, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from collections import namedtuple
from sklearn.decomposition import PCA
from os import cpu_count
from TwoGroupsWeightedModel import TwoGroupsWeightedModel
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier


def get_best_roc(models, train_X, train_y, test_X, test_y):
    best_score = -1*float('inf')
    for model in models:
        model.fit(train_X, train_y)
        predicted_probs = model.predict_proba(test_X)[:,1]
        scr = roc_auc_score(y_true=test_y, y_score=predicted_probs)
        if scr > best_score:
            best_score = scr
            best_model = model
    return best_score, best_model


def evaluate_classifier_cv(clf, X, y, cross_validation_folds=10,random_split=True, round_result_to=4, scoring='accuracy'):
    """
    :param clf: a classifier that inherrits from sklearn's BaseClassifier
    :param X: pandas df of explanatory variables
    :param y: target column
    :param cross_validation_folds: number of folds for k-fold cross-validation
    :return: prints train accuracy on the entire dataset, and the test accuracy calculated with k-fold cross validation
    """
    cv_gen = KFold(n_splits=cross_validation_folds, shuffle=random_split)
    test_accuracy = np.mean(cross_val_score(estimator=clf, X=X, y=y, cv=cv_gen, scoring=scoring))
    clf.fit(X, y)
    train_accuracy = clf.score(X, y)
    res = namedtuple("accuracy", "test train test_score train_score")
    res.test = "Test accuracy ({}-fold cross validation):".format(cross_validation_folds)+str(round(test_accuracy, round_result_to))
    res.train = "Train accuracy:"+str(round(train_accuracy, round_result_to))
    res.test_score = test_accuracy
    res.train_score = train_accuracy
    return res


def split_to_train_test_and_apply_scaling_and_lda_dim_reduction(X, y, train_percentage):
    """
    :param train_percentage: what percentage of the data will be used for train (the rest - for test)
    :return: retunrs train and test sets, after applying sklearn's standard-scalar and LDA dimensionality reduction.

    This function is used to explicitly avoid using sklearn's LDA API for dim-reduction, which we find confusing and
    believe is the source for the error in the original article.
    """
    lda = LinearDiscriminantAnalysis()
    scaler = StandardScaler()
    indices = [i for i in range(len(y))]
    train_indices = np.random.choice(indices, size=int(train_percentage * len(y)), replace=False)
    test_indices = [i for i in indices if i not in train_indices]

    train_X = scaler.fit_transform(X.iloc[train_indices])
    train_y = y.iloc[train_indices].values.reshape(-1, 1)

    test_X = scaler.transform(X.iloc[test_indices])
    test_y = y.iloc[test_indices].values.reshape(-1, 1)

    train_X = lda.fit_transform(train_X, train_y)
    test_X = lda.transform(test_X)

    return train_X, train_y, test_X, test_y

def plot_labeled_data_1d(reduced_X, y, title, group_labels =("diagnosed", "not_diagnosed"), show=False):
    pdt = [reduced_X[i] for i in range(len(reduced_X)) if y.values[i] == True]
    pdf = [reduced_X[i] for i in range(len(reduced_X)) if y.values[i] == False]
    a = plt.scatter(pdf, [0 for i in range(len(pdf))])
    b = plt.scatter(pdt, [0 for i in range(len(pdt))], color="red")
    plt.title(title)
    plt.legend([b, a], group_labels)
    if show:
        plt.show()


def plot_labeled_data_2d(reduced_X, y, title, group_labels =("diagnosed", "not_diagnosed"), show=False):
    x1_pd_true = [reduced_X[i][0] for i in range(len(y)) if y.values[i] == True]
    x1_pd_false = [reduced_X[i][0] for i in range(len(y)) if y.values[i] == False]
    x2_pd_true = [reduced_X[i][1] for i in range(len(y)) if y.values[i] == True]
    x2_pd_false = [reduced_X[i][1] for i in range(len(y)) if y.values[i] == False]
    b = plt.scatter(x1_pd_true, x2_pd_true, color='red')
    a = plt.scatter(x1_pd_false, x2_pd_false, color='blue')
    plt.title(title)
    plt.legend([b, a], group_labels)
    if show:
        plt.show()


def plot_labeled_data_3d(reduced_X, y, title, group_labels =("diagnosed", "not_diagnosed"), show=False):
    x1_pd_true = [reduced_X[i][0] for i in range(len(y)) if y.values[i] == True]
    x1_pd_false = [reduced_X[i][0] for i in range(len(y)) if y.values[i] == False]
    x2_pd_true = [reduced_X[i][1] for i in range(len(y)) if y.values[i] == True]
    x2_pd_false = [reduced_X[i][1] for i in range(len(y)) if y.values[i] == False]
    x3_pd_true = [reduced_X[i][2] for i in range(len(y)) if y.values[i] == True]
    x3_pd_false = [reduced_X[i][2] for i in range(len(y)) if y.values[i] == False]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    a = ax.scatter(x1_pd_false, x2_pd_false, x3_pd_false, c='blue')
    b = ax.scatter(x1_pd_true, x2_pd_true, x3_pd_true, c='red')
    plt.title(title)
    plt.legend([b, a], group_labels)
    if show:
        plt.show()