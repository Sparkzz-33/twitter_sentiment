# -*- coding: utf-8 -*-
"""
Created on Mon May 18 18:22:29 2020

@author: Ashutosh Rajput (CS17B007)
"""

import flask
from twitterscraper import query_tweets
import datetime as dt
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from flask import send_file
import pickle 
def detector(x):
    try:
        return detect(x)
    except:
        None

app = flask.Flask(__name__, template_folder='templates')



@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('main.html'))
    
    if flask.request.method == 'POST':
        
        hashtag = flask.request.form['hashtag']
        begin_date = dt.date(2020,4,30)
        end_date = dt.date(2020,5,1)
        limit = 100
        lang = 'english'
            
        analyzer = SentimentIntensityAnalyzer()
            
        tweets = query_tweets(hashtag, begindate = begin_date, enddate = end_date, limit = limit, lang = lang)        
            
        df = pd.DataFrame(t.__dict__ for t in tweets)
    
        df['lang'] = df['text'].apply(lambda x:detector(x))
        df = df[df['lang'] == 'en']
            
        sentiment = df['text'].apply(lambda x: analyzer.polarity_scores(x))
            
        df = pd.concat([df, sentiment.apply(pd.Series)], 1)
        df.drop_duplicates(subset = 'text', inplace = True)
            
        score = df['compound']
        np_hist = np.array(score)
        print("here ", len(score))
        hist,bin_edges = np.histogram(np_hist)
        print(bin_edges)
            
        plt.figure(figsize=[18,15])
            
        plt.bar(bin_edges[:-1], hist, width = 0.1,color='#0504aa',alpha=0.7)
        plt.xlim(min(bin_edges), max(bin_edges))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Compound Score',fontsize=15)
        plt.ylabel('Total Tweets',fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.title('Sentimental Intensity Distribution for '+hashtag,fontsize=15)
        output = BytesIO()
        plt.savefig(output, format='png')
        output.seek(0)
        pickle_out = open("image_object.pickle", "wb")
        pickle.dump(output, pickle_out)
        pickle_out.close()
        print("reached here")
        print("Current method: ", flask.request.method)
        return flask.render_template('output.html', result = 1, name = hashtag)
    
@app.route("/images/output_plot", methods=['GET', 'POST'])
def output_plot():
    print("here too MF")
    pickle_in = open("image_object.pickle", "rb")
    pickle_in.seek(0)
    output = pickle.load(pickle_in)
    now = dt.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    return send_file(output, attachment_filename='plot.png', mimetype='image/png')
    
    
   
if __name__ == '__main__':
    app.run()