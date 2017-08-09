#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 18:20:32 2017

@author: shayneufeld
"""
import pandas as pd
import numpy as np
import pickle


#variables to load in
artist_table = pd.read_csv('../data/artist_table.csv',index_col=0)
als_model = pickle.load(open('../models/als_model.sav', 'rb'))
forest_model = pickle.load(open('../models/rf_model.sav','rb'))
album_features = pd.read_csv('../data/album_features.csv',index_col=0)
prices_genres_features = np.loadtxt('../data/prices_genres_features.csv')
sales_df = pd.read_csv('../data/sales.csv',index_col=0)


def predictNumBuyers(artist_key=[], model = forest_model,features=prices_genres_features,data=album_features):
    #use random forest classifier to predict how an album will sell
    #the classifier uses item types + prices, as well as a dimensionality 
    #reduced form of the genre tags as features, and returns a prediction of
    #sales as:
        # low ( <100)
        # med (100-500)
        # hi  (>500)
        
    x = features[artist_key,:]
    y_predict = model.predict(x)
    
    return y_predict[0]
    

def getRelatedArtists(artist_key=[],model=als_model,data=artist_table):
    #use alternating least squares matrix factorization to identify
    #similar artists
    als_result = model.similar_items(artist_key,N=50)

    results = als_result
    als_ = pd.DataFrame()

    for als_r in results[1:]: #exclude the artist in question
        als_ = als_.append(artist_table[artist_table.artist_id==als_r[0]])
        
    related_artists = als_.name.values
    
    return related_artists


def getRelatedSales(related_artists = [],sales=sales_df):
    # based on related artists, search for all sales made by those 
    # related artists that have been captured in the sales table.
    related_sales_als = pd.DataFrame()

    for als_artist in related_artists:
        related_sales_als_ = sales[sales.artist_name==als_artist].copy()
        related_sales_als = related_sales_als.append(related_sales_als_)
        
    return related_sales_als


def recommendPrices(related_sales = []):  
    #based on the related sales, determine the best products and prices
    #that would account for the most revenue
    item_types = related_sales.item_type.unique()


    price_analysis = pd.DataFrame(data=None,index=['Price','Revenue','Frac_Revenue'],columns=['a','b','t','p'])
    
    for i,item_type in enumerate(item_types):
        test=related_sales[related_sales.item_type==item_type]
        x = np.histogram(test.amount_paid_usd.values)[1][:-1]
        y = np.histogram(test.amount_paid_usd.values)[0]*x
        
        opt = x[np.where(y==y.max())]
        rev = y.max()
        price_analysis.loc['Price',item_type] = np.round(opt[0])
        price_analysis.loc['Revenue',item_type] = rev
        
    #get fraction of revenue for each type
    price_analysis.loc['Frac_Revenue',:] = price_analysis.loc['Revenue',:].values / price_analysis.loc['Revenue',:].values.sum(axis=0)
    
    rec = pd.DataFrame()
    for col in price_analysis.columns.values:
        if price_analysis.loc['Frac_Revenue',col] > 0.2:
            rec = rec.append(price_analysis[col])
    
    #re-normalize the fraction revenue column to sum to 1 with the recomended items
    rec['Frac_Revenue'] = np.round(rec.Frac_Revenue.values / rec.Frac_Revenue.values.sum(),2)
    
    #add type of item to the dataframe
    items = []
    for item in rec.index.values:
        if item == 'a':
            items.append('digital download')
        elif item == 'p':
            items.append('physical album')
        elif item == 'b':
            items.append('bundle of merch')
        elif item == 't':
            items.append('track download')
    
    rec['Type'] = items
    rec = rec.drop('Revenue',axis=1)
    return rec


def predictRevenue(rec_items=[],num_sales=[]):
    
    lower_bound,upper_bound = 0,0
    lower,higher = 0,0
    
    if num_sales == 'low':
        lower = 0
        higher = 100
    
    elif num_sales == 'med':
        lower = 100
        higher = 500
        
    elif num_sales == 'hi':
        lower = 500
        higher = 0
        
        
    for item in rec_items.iterrows():
        lower_bound += lower*item[1].Price
        upper_bound += higher*item[1].Price
    
    revenue = []
    if num_sales == 'low':
        revenue = '$<' + str(np.round(upper_bound))
    elif num_sales == 'med':
        revenue = '$ ' + str(np.round(lower_bound)) + ' - ' + str(np.round(upper_bound,0))
    elif num_sales == 'hi':
        revenue = '$>' + str(np.round(lower_bound))
    else:
        'Error: bad input'
    
    return revenue


def getArtistKey(artist_name = [],data=artist_table):
    #find the artist id corresponding to the artist name
    #this id is required for using the als model
    return data[data.name==artist_name].artist_id.values[0]
