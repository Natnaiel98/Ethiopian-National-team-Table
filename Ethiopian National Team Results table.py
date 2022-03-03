# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 11:26:20 2022

@author: natem
"""
#This code obtains the information from the webstite National Football Teams
#and produces a dictionary with dataframes that cover the Ethiopian National Teams results
# as well as auxillary information such as the city and stadium the game took place in from 
#2010 to 2022

import io   
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import selenium
import matplotlib.pyplot as plt
import re
import datetime


headers = {'User-Agent': 
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

#retrieving national team data from the 'National Football teams website'    
#storing the tables in different tables for the different years
results={}
for  i in range(2010,2023):
    link='https://www.national-football-teams.com/country/63/' + str(i)+ '/Ethiopia.html'
    pageTree = requests.get(link, headers=headers)
    #parses the collected html data
    pageSoup = BeautifulSoup(pageTree.text, 'html.parser')
    tables=pageSoup.find_all("table",{"class":"data-table"})
    #reads all off our text code as a dataframe(only need the first table as this is the results table)
    fin=pd.read_html(str(tables))[0]
    #update the dictionary with our table
    results["table" +str(i)]=fin
    
   #We need to modify each dataframe to add city,country,stadium information
   #in each table code, the Stadium itself has a link that redirects to a page with the city name
   #Making city and countries dictionaries with the keys as stadiums makes them easy to merge with the main table later
    city={}
    country={}
    link2='https://www.national-football-teams.com'
    stadium=pageSoup.find_all("td",{"class":"stadium"}) 
    
    #obtaining the stadiums matches were played in
    stad=[]
    for p in pageSoup.find_all('a', href=True):
      if 'stadium' in p['href']:
          stad.append (p['href'])    
    
    #code to obtain the city from the stadium name
    for a in stad:

        link3= link2 + a
        pageTree = requests.get(link3, headers=headers)
        #parses the collected html data
        pageSoup = BeautifulSoup(pageTree.text, 'html.parser')
        stad2=pageSoup.find_all("h1")
        cty=pageSoup.find_all("div",{"class":"col-6"})
        city[stad2[0].text.strip()]=((cty[-3].text.strip()))
        country[stad2[0].text.strip()]=((cty[-1].text.strip()))
    
    #make sure that missing values are handled
    #missing values causing issues

    for cit in city.values():
        if cit=='-':
            city[stad2[0].text.strip()]=stad2[0].text.strip()
            
    #adding a column with the city name for each dataframe
    #but first drop the last row of each data frame, does not contain any necessary information
    results["table" +str(i)]=results["table" +str(i)].drop(results["table" +str(i)].index[-1])
    #getting city name based on our key of stadium matching stadium name of table
    results["table"+str(i)]['City'] = results["table"+str(i)]['Stadium'].apply(lambda x: city.get(x))
    #getting country name based on our key of stadium matching stadium name of table
    results["table"+str(i)]['Country'] = results["table"+str(i)]['Stadium'].apply(lambda x: country.get(x))
    #adding month row, city is a dict with stadium name and city
    results["table" +str(i)]['Month']=results["table" +str(i)]['Date'].apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%d').strftime("%b"))
    
    #split up the result column into home and away score and convert columns into numeric for later analysis
    results["table" +str(i)]['Home Score']=results["table" +str(i)]['Result'].apply(lambda x: x.split(':')[0].strip(),pd.to_numeric)
    results["table" +str(i)]['Away Score']=results["table" +str(i)]['Result'].apply(lambda x: x.split(':')[1][:-2].strip(),pd.to_numeric)
    


