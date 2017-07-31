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
    
    def __init__(self,start_urls='',*args,**kwargs):
        
        self.driver = webdriver.Firefox() #use selenium driver
        #self.start_urls = start_urls
        #self.album_name = album_name
        #self.artist_name = artist_name
        
        #clean up urls
        #start_urls = start_urls.replace("[",'')
        #start_urls = start_urls.replace("]",'')
        #start_urls = start_urls.replace("'",'')
        #start_urls = start_urls.replace(" ",'')
        #start_urls = start_urls.split(',')
        
        self.start_urls = [start_urls]
        
        super(BandCampSpider, self).__init__(**kwargs)
        
    def parse(self,response):
        
        self.driver.get(response.url)
        
        #expand page to reveal all supporters
        expand_supporters(self)
        
        #update response to include the 'more' clicks
        response = scrapy.Selector(text=self.driver.page_source)
        
        #get artist name
        artist_name_section = response.css('div#name-section')
        artist_name = artist_name_section.css('a::text').extract()[0]
        
        #get album name
        album_name = response.css('h2.trackTitle::text')[0].extract()
        #have to clean it up...
        album_name = album_name.replace(' ','')
        album_name = album_name.replace('\n','')
        
        album_info_df = get_items_tags(response,artist_name,album_name)
        
        
        
        '''
        CONTRIBUTOR INFORMATION
        '''
        # contrib_name,contrib_url = get_contributors(response)
        # add_contributors_to_db(contrib_name,contrib_url)
        
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
        df['artist_name'] = artist_name
        df['album_name'] = album_name        
        df['album_url'] = self.start_urls[0]
        
        # save dataframe
        file_name = '/Users/shayneufeld/dropbox/insight/pricecamp/data/albums_supporters/%s-%s.csv' % (album_name,artist_name)
        file_name = file_name.replace(',','')
        file_name = file_name.replace(' ','')
        df.to_csv(file_name)
        
        
        #save album info dataframe - same name, different folder
        file_name = '/Users/shayneufeld/dropbox/insight/pricecamp/data/albums_info/%s-%s.csv' % (album_name,artist_name)
        file_name = file_name.replace(',','')
        file_name = file_name.replace(' ','')
        album_info_df.to_csv(file_name)
        
        #close down the driver
        self.driver.close()
        

## FUNCTIONS

def get_items_tags(response,artist_name,album_name):
    
    item_types = response.css('span.buyItemPackageTitle::text')
    item_prices = response.css('span.base-text-color::text')
    items_df = pd.DataFrame()
    items_df.loc[0,'album_name'] = album_name
    items_df.loc[0,'artist_name'] = artist_name
    
    for i_type,i_price in zip(item_types,item_prices):
        i_type_str = i_type.extract()
        i_type_price = i_price.extract()
        
        #put into dataframe
        items_df.loc[0,i_type_str] = i_type_price
        
    tag_elem = response.css('a.tag::text')
    tags = []
    
    for elem in tag_elem:
        tags.append(elem.extract())
    
    items_df.loc[0,'tags'] = str(tags[:-1])
    items_df.loc[0,'location'] = str(tags[-1])
    
    #finally, get date:
    date_mess = response.css('div.tralbumData.tralbum-credits::text').extract()[0]
    date_mess = date_mess.replace('\n','')
    date_mess = date_mess.replace(' ','')
    date_mess = date_mess.replace('released','')
    date = date_mess[-4:]
    items_df.loc[0,'year'] = date
    
    return(items_df)
    


def expand_supporters(selenium_driver):
#click through more buttons on the album page
    more_thumbs_el,more_writing_el = [],[]
    
    #see if there are any 'more thumbs' if so, retrieve the elements
    try:
        more_thumbs_el = selenium_driver.driver.find_element_by_css_selector('.more-thumbs')
    except:
        pass
    #see if there are any 'more comments' if so, retrieve the elements
    try:
        more_writing_el = selenium_driver.driver.find_element_by_css_selector('.more-writing')
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