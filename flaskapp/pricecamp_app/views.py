#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:51:32 2017

@author: shayneufeld
"""
from flask import render_template
from pricecamp_app import app
from pricecamp_app.a_Model import predictNumBuyers
from pricecamp_app.a_Model import getRelatedArtists
from pricecamp_app.a_Model import predictBestPrice
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request 

user = 'shayneufeld' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'music_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Shay' },
       )

@app.route('/db')
def artist_page(): #was birth page
    sql_query = """                                                                       
                SELECT * FROM artist_table_trimmed;          
                """
    query_results = pd.read_sql_query(sql_query,con)
    popular_artists_inds = query_results.bc_avg_supporters.sort_values(ascending=False).index.values
    popular_artists = query_results.loc[popular_artists_inds,'bc_artist']
    d = {'artist':popular_artists,'num_followers':query_results.bc_avg_supporters.sort_values(ascending=False).values}

    return popular_artists.values[0]
    
    
@app.route('/input')
def artist_input():
    return render_template("input.html")

@app.route('/output')
def artist_output():
  #pull 'birth_month' from input field and store it
  artist_name = request.args.get('artist_name')
    #just select the Cesareans  from the birth dtabase for the month that the user inputs
  query = "SELECT * FROM artist_table_trimmed WHERE bc_artist='%s'" % artist_name
  print(query)
  query_results=pd.read_sql_query(query,con)
  print(query_results)
  results = getRelatedArtists(artist_name)
  print(results)
  related_artists = []
  for i in range(0,results.shape[0]):
      related_artists.append(dict(search_artist=artist_name,artist=results.iloc[i]['bc_artist'], num_buyers=results.iloc[i]['bc_num_supporters'],revenue=results.iloc[i]['bc_num_supporters']*results.iloc[i]['sales_avgprice'],price=results.iloc[i]['sales_avgprice']))
      the_result = ''
  the_result = predictNumBuyers(artist_name=artist_name,rel_artists = results)
  print(the_result[0])
  print(the_result[0] > 100)
  price = predictBestPrice(y_predict = the_result[0])
  print(related_artists)
  
  return render_template("output.html", artists = related_artists, the_result = the_result,price=price)