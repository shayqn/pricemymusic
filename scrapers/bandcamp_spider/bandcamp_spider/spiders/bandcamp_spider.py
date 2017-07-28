#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 21:24:44 2017

@author: shayneufeld
"""

import scrapy
from selenium import webdriver
import time
import pandas as pd

class BandCampSpider(scrapy.Spider):
    '''
    BandCampSider uses selenium to crawl through an album page on bandcamp, 
    click through the 'more' buttons to revea lall the supporters, and then
    scrapes each supporter and saves it to a csv file.
    '''
    
    name = "bandcamp"
    allowed_domain = ['bandcamp.com']
    
    def __init__(self,start_domain='',album_name = '',artist_name='',*args,**kwargs):
        
        self.driver = webdriver.Firefox() #use selenium driver
        self.start_urls = [start_domain]
        self.album_name = album_name
        self.artist_name = artist_name
    
    def parse(self,response):
        self.driver.get(response.url)
        more_thumbs_el,more_writing_el = [],[]
        
        #see if there are any 'more thumbs' if so, retrieve the elements
        try:
            more_thumbs_el = self.driver.find_element_by_css_selector('.more-thumbs')
        except:
            pass
        #see if there are any 'more comments' if so, retrieve the elements
        try:
            more_writing_el = self.driver.find_element_by_css_selector('.more-writing')
        except:
            pass
        
        #loop through the 'more' buttons and press them
        if more_thumbs_el or more_writing_el:
            # open up all the contributors for the album
            for el in [more_writing_el,more_thumbs_el]:
                while True:
                    try:
                        el.click()
                        time.sleep(1)
                    except:
                        break
            #update response to include the 'more' clicks
            response = scrapy.Selector(text=self.driver.page_source)
        
        #NOTE: I'm not sure if this will work if there are more thumbs
        # but not more comments or vice versa. But I think it will..
        
        '''
        CONTRIBUTOR INFORMATION
        '''
        contrib_name,contrib_url = [],[]
        
        
        # SCRAPING:
        # so now we need to use scrapy to store:
            # contributor name, contributor url
        
        #there are two types of contributors on the bandcamp page:
            # contributors with comments
            # contributors without comments
        
        #CONTRIBUTORS WITH COMMENTS
        writing_els = response.css('div.writing') #all the writing contributors
        
        #then need to loop through
        for el in writing_els:
            contrib_name.append(el.css('div.name::text').extract()) #contributor name
            contrib_url.append(el.css('a::attr(href)').extract_first()) #contributor link
        

        #CONTRIBUTORS WITHOUT COMMENTS
        no_writing_els = response.css('div.no-writing')
        contrib_name_els = no_writing_els.css('div.round3')
        contrib_url_els = no_writing_els.css('a::attr(href)')
        
        #then need to loop through
        for name,url in zip(contrib_name_els,contrib_url_els):
            contrib_name.append(name.css('div.name::text').extract()) #contributor name
            contrib_url.append(url.extract())
        
        
        # construct dataframe
        df = pd.DataFrame(data=None,columns=['artist_name','contrib_name','contrib_url','album_name','album_url'])
        df['contrib_name'] = contrib_name
        df['contrib_url'] = contrib_url
        df['artist_name'] = self.artist_name
        df['album_name'] = self.album_name        
        df['album_url'] = self.start_urls[0]
        
        #only save if there are at least 10 contributors:
        if df.shape[0] >= 10:
            file_name = '/Users/shayneufeld/dropbox/insight/pricecamp/data/albums_fixed/%s-%s.csv' % (self.album_name,self.artist_name)
            file_name = file_name.replace(',','')
            file_name = file_name.replace(' ','')
            df.to_csv(file_name)
        
        #close down the driver
        self.driver.close()