#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:51:32 2017

@author: shayneufeld
"""
from flask import render_template
from pricecamp_app import app
import pricecamp_app.Models as pc 
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request 
from flask import send_file

#user = 'shayneufeld' #add your username here (same as previous postgreSQL)                      
#host = 'localhost'
#dbname = 'music_db'
#db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#con = None
#con = psycopg2.connect(database = dbname, user = user)


@app.route('/')
@app.route('/index')
def index():

    return render_template("input.html")

@app.route('/graphic',methods=['GET'])
def get_image():
 filename = 'static/graphics/pmm_graphic.png'
 return send_file(filename, mimetype='image/png')
    
    
@app.route('/input')
def artist_input():

    return render_template("input.html")

@app.route('/output')
def artist_output():
  #pull 'birth_month' from input field and store it
  artist_name = request.args.get('artist_name')
  artist_key = pc.getArtistKey(artist_name)
  related_artists = pc.getRelatedArtists(artist_key=artist_key)
  related_sales = pc.getRelatedSales(related_artists=related_artists)
  rec_items = pc.recommendPrices(related_sales=related_sales)
  num_sales = pc.predictNumBuyers(artist_key=artist_key)
  predicted_revenue = pc.predictRevenue(rec_items=rec_items,num_sales=num_sales)
  recommend = []
  
  for i in range(0,rec_items.shape[0]):
      recommend.append(dict(search_artist=artist_name,item_type=rec_items.iloc[i]['Type'],item_price=rec_items.iloc[i]['Price'],item_frac = rec_items.iloc[i]['Frac_Revenue']))
  
  return render_template("output.html", predicted_revenue=predicted_revenue,recommend=recommend)