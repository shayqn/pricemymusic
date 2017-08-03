#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 14:57:13 2017

@author: shayneufeld
"""
import pandas as pd
from sklearn import linear_model
import numpy as np

all_genres = pd.read_csv('/Users/shayneufeld/Dropbox/insight/pricecamp/all_genres.csv',index_col=0)
data = pd.read_csv('/Users/shayneufeld/Dropbox/insight/pricecamp/master_table_trimmed.csv',index_col=0)
features = ['sp_popularity','sp_num_followers']
supporters_sparse = scipy.sparse.load_npz('/Users/shayneufeld/Dropbox/insight/pricecamp/data/supporters_sparse_matrix.npz')
artist_table = pd.read_csv('/Users/shayneufeld/Dropbox/insight/pricecamp/data/artist_table.csv')

def predictNumBuyers(fromUser  = 'Default', rel_artists = [],artist_name=[],data=data,features=features):
    x = rel_artists.loc[:,features].values
    y = rel_artists.bc_avg_supporters.values
    reg = linear_model.LinearRegression(normalize=True)
    reg.fit(x,y)
    
    [x_test,y_test] = get_features(artist_name,data,features)
    y_predict = reg.predict(x_test)
    
    return [np.round(y_predict),np.round(y_test)]

def predictBestPrice(fromUser  = 'Default',y_predict=0):

    if y_predict < 100:
        price = 5
    elif y_predict > 300:
        price = 7
    else:
        price = 12
    
    return price


def getRelatedArtists(artist_name,data=supporters_sparse):

    artist_factors, _, user_factors = linalg.svds(bm25_weight(data), 50)
    
    toprelated = TopRelated(artist_factors)
    result = toprelated.get_related(678,N=21)
    related_artists = []
    related_tags = []
    for r in result:
        rel_artist = artist_table[artist_table.artist_id==r]
        artist_name = rel_artist.artist_name.values
        tags = rel_artist.tags.values
        related_artists.append(artist_name)
        related_tags.append(tags)
    
    results = related_artists[1:] #remove self from list
    
    return results

def get_features(artist_name,data,features): 
    x_test = data.loc[data.bc_artist == artist_name,features].values
    y_test = data.loc[data.bc_artist == artist_name,'bc_avg_supporters'].values
    
    return x_test,y_test

"""
Functions for retrieving related artists
"""
from scipy.sparse import coo_matrix
import scipy
from scipy.sparse import linalg

def bm25_weight(X, K1=100, B=0.8):
    """ Weighs each row of a sparse matrix X  by BM25 weighting """
    # calculate idf per term (user)
    X = coo_matrix(X)

    N = float(X.shape[0])
    idf = np.log(N / (1 + np.bincount(X.col)))

    # calculate length_norm per document (artist)
    row_sums = np.ravel(X.sum(axis=1))
    average_length = row_sums.mean()
    length_norm = (1.0 - B) + B * row_sums / average_length

    # weight matrix rows by bm25
    X.data = X.data * (K1 + 1.0) / (K1 * length_norm[X.row] + X.data) * idf[X.col]
    return X


class TopRelated(object):
    def __init__(self, artist_factors):
        # fully normalize artist_factors, so can compare with only the dot product
        norms = np.linalg.norm(artist_factors, axis=-1)
        self.factors = artist_factors / norms[:, np.newaxis]

    def get_related(self, artistid, N=20):
        scores = self.factors.dot(self.factors[artistid])
        best = np.argpartition(scores, -N)[-N:]
        return sorted(zip(best, scores[best]), key=lambda x: -x[1])