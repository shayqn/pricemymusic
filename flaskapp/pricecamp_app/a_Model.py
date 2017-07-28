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


def getRelatedArtists(artist_name,data=data,all_genres=all_genres):
    df = data.copy()
    artist_genres_str = df[df.bc_artist == artist_name].sp_genres.values[0]
    
    artist_genres = artist_genres_str.replace('[','')
    artist_genres = artist_genres.replace(']','')
    artist_genres = artist_genres.split(sep=',')
    
    hits = []
    for genre in artist_genres:
        for i,genre_str in enumerate(data.sp_genres.values):
            if genre in genre_str:
                hits.append(i)
    
    results = df.iloc[hits].drop_duplicates()
    
    results = results[results.bc_artist != artist_name] #remove self from list
    
    return results

def get_features(artist_name,data,features): 
    x_test = data.loc[data.bc_artist == artist_name,features].values
    y_test = data.loc[data.bc_artist == artist_name,'bc_avg_supporters'].values
    
    return x_test,y_test