from __future__ import print_function

import logging
import numpy as np
from optparse import OptionParser
import sys
from time import time
import matplotlib.pyplot as plt

from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.utils.extmath import density

from scikit_utilities import StemmedTfidfVectorizer, get_cluster_data, associate_post_with_cluster

import django
django.setup()
from django.conf import settings
if not settings.configured:
    settings.configure(
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'restorestemmedbody.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
            'PORT': '3306',
            'USER': 'teamamzn',
            'PASSWORD': 'TeamAmazon2015!',
            'NAME': 'sellerforums',
            'OPTIONS': {
                'autocommit': True,
            },
        }
        }
    )

NUM_FEATURES = 1000
IS_REPORT_PRINTED = True
IS_CONFUSION_MATRIX_PRINTED = True
IS_CHI_SQUARED_USED = False
IS_IDF_USED = True
IS_UPLOAD_ENBABLED = True
IS_PLOTTING_ON = False
IS_PLOTTING_ON = False


class L1LinearSVC(LinearSVC):

    def fit(self, X, y):
        # The smaller C, the stronger the regularization.
        # The more regularization, the more sparsity.
        self.transformer_ = LinearSVC(penalty="l1",
                                      dual=False, tol=1e-3)
        X = self.transformer_.fit_transform(X, y)
        return LinearSVC.fit(self, X, y)

    def predict(self, X):
        X = self.transformer_.transform(X)
        return LinearSVC.predict(self, X)


def classify_on_date_range(train_start_date, train_end_date, new_start_date, new_end_data):
    data_train = get_cluster_data(train_start_date, train_end_date)
    data_test = get_cluster_data(new_start_date, new_end_data)

    categories = data_train.cluster_list

    X_test, X_train, vectorizer, y_train = vectorize(data_test, data_train)

    if IS_CHI_SQUARED_USED:
        chi_squared_transformer(X_test, X_train, y_train)

    # mapping from integer feature name to original token string
    feature_names = np.asarray(vectorizer.get_feature_names())

    classify(L1LinearSVC(), data_test, X_train, y_train, X_test, feature_names, categories)

    if IS_UPLOAD_ENBABLED:
        associate_post_with_cluster(data_test, len(categories), new_start_date, new_end_data)


def vectorize(data_test, data_train):
    # list of cluster associated with each posts
    y_train = data_train.cluster_of_posts
    print("Extracting features from the training dataset using a sparse vectorizer")
    t0 = time()
    vectorizer = StemmedTfidfVectorizer(max_df=.8, max_features=NUM_FEATURES,
                                        min_df=1,
                                        use_idf=IS_IDF_USED, analyzer='word', ngram_range=(1, 1))
    # Create training data
    X_train = vectorizer.fit_transform(data_train.data)
    # Create data to classify
    X_test = vectorizer.transform(data_test.data)
    return X_test, X_train, vectorizer, y_train


def chi_squared_transformer(X_test, X_train, y_train):
    t0 = time()
    ch2 = SelectKBest(chi2, k=NUM_FEATURES)
    X_train = ch2.fit_transform(X_train, y_train)
    X_test = ch2.transform(X_test)
    print()


def trim(s):
    """Trim string to fit on terminal (assuming 80-column display)"""
    return s if len(s) <= 80 else s[:77] + "..."


def classify(clf, cluster_data, X_train, y_train, X_test, feature_names, categories):
    print('_' * 80)
    print("Training: ")
    print(clf)
    t0 = time()
    clf.fit(X_train, y_train)
    train_time = time() - t0
    print("train time: %0.3fs" % train_time)

    t0 = time()
    cluster_data.cluster_of_posts = clf.predict(X_test)
    test_time = time() - t0
    print("test time:  %0.3fs" % test_time)

    if hasattr(clf, 'coef_'):
        print("dimensionality: %d" % clf.coef_.shape[1])
        print("density: %f" % density(clf.coef_))

        if feature_names is not None:
            print("top 10 keywords per class:")
            for i, category in enumerate(categories):
                top10 = np.argsort(clf.coef_[i])[-10:]
                print(trim("%s: %s"
                           % (category, " ".join(feature_names[top10]))))
        print()

    if IS_REPORT_PRINTED:
        print("classification report:")

    print()
    clf_descr = str(clf).split('(')[0]
    return clf_descr, train_time, test_time


def main():

    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    print()

    data_train = get_cluster_data("2014-01-01", "2014-02-01")
    new_start_date = "2013-02-01"
    new_end_date = "2013-03-03"
    data_test = get_cluster_data(new_start_date, new_end_date)
    print('data loaded')
    categories = data_train.cluster_list

    X_test, X_train, vectorizer, y_train = vectorize(data_test, data_train)
    # Here down is essentially black magic... But I suppose it works
    if IS_CHI_SQUARED_USED:
        chi_squared_transformer(X_test, X_train, y_train)



    # mapping from integer feature name to original token string
    feature_names = np.asarray(vectorizer.get_feature_names())
    results = []
    # for clf, name in (
    #         (RidgeClassifier(tol=1e-2, solver="lsqr"), "Ridge Classifier"),
    #         (Perceptron(n_iter=50), "Perceptron"),
    #         (PassiveAggressiveClassifier(n_iter=50), "Passive-Aggressive")):
    #     # (KNeighborsClassifier(n_neighbors=10), "kNN")):
    #     print('=' * 80)
    #     print(name)
    #     results.append(classify(clf, data_test))
    # for penalty in ["l2", "l1"]:
    #     print('=' * 80)
    #     print("%s penalty" % penalty.upper())
    #     # Train Liblinear model
    #     results.append(classify(LinearSVC(loss='l2', penalty=penalty,
    #                                       dual=False, tol=1e-3), data_test))
    #
    #     # Train SGD model
    #     results.append(classify(SGDClassifier(alpha=.0001, n_iter=50,
    #                                           penalty=penalty), data_test))
    #
    # # Train SGD with Elastic Net penalty
    # print('=' * 80)
    # print("Elastic-Net penalty")
    # results.append(classify(SGDClassifier(alpha=.0001, n_iter=50,
    #                                       penalty="elasticnet"), data_test))
    # # Train NearestCentroid without threshold
    # print('=' * 80)
    # print("NearestCentroid (aka Rocchio classifier)")
    # results.append(classify(NearestCentroid(), data_test))
    # # Train sparse Naive Bayes classifiers
    # print('=' * 80)
    # print("Naive Bayes")
    # results.append(classify(MultinomialNB(alpha=.01), data_test))
    # results.append(classify(BernoulliNB(alpha=.01), data_test))



    print('=' * 80)
    print("LinearSVC with L1-based feature selection")
    results.append(classify(L1LinearSVC(), data_test, X_train, y_train, X_test, feature_names, categories))
    # make some plots
    if IS_PLOTTING_ON:

        indices = np.arange(len(results))

        results = [[x[i] for x in results] for i in range(3)]

        clf_names, training_time, test_time = results
        training_time = np.array(training_time) / np.max(training_time)
        test_time = np.array(test_time) / np.max(test_time)

        plt.figure(figsize=(12, 8))
        plt.title("Score")

        plt.barh(indices + .3, training_time, .2, label="training time", color='g')
        plt.barh(indices + .6, test_time, .2, label="test time", color='b')
        plt.yticks(())
        plt.legend(loc='best')
        plt.subplots_adjust(left=.25)
        plt.subplots_adjust(top=.95)
        plt.subplots_adjust(bottom=.05)

        for i, c in zip(indices, clf_names):
            plt.text(-.3, i, c)

        plt.show()
    if IS_UPLOAD_ENBABLED:
        associate_post_with_cluster(data_test, len(categories), new_start_date, new_end_date)


main()