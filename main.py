from pymongo import MongoClient
import pymongo
import csv
import json
import pandas as pd
import sys, getopt, pprint
import os


from collections import defaultdict
import yfinance as yf
import re

#This resets the database maindata
def reset_table():
    csvfile = open('maindata.csv', 'r')
    reader = csv.DictReader(csvfile)
    mng_db=mongo_client['project3']
    db = mng_db['stocktweets']
    db.drop()
    header= [ "id", "text", "timestamp" , "source", "symbols", "company_names", "url", "verified"]

    for each in reader:
        row={}
        for field in header:
            row[field]=each[field]

        db.insert(row)

    for data in mongo_client.list_databases():
        print(data)
    return db

#Main influencers who mostly have verified tweets, this can be used to simplify function calls
main_influencers = ['MarketWatch', 
'business', 'YahooFinance', 'TechCrunch', 'WSJ', 'Forbes', 
'FT', 'TheEconomist', 'nytimes', 'Reuters', 'GerberKawasaki', 
'jimcramer', 'TheStreet', 'TheStalwart', 'TruthGundlach', 'CarlCIcahn', 
'ReformedBroker', 'benbernanke', 'bespokeinvest', 'BespokeCrypto', 
'stlouisfed', 'federalreserve', 'GoldmanSachs', 'ianbremmer', 
'MorganStanley', 'AswathDamodaran', 'mcuban', 'muddywatersre', 
'StockTwits', 'SeanaNSmith']

#Filter and create new collection based on elements of idarray where other records in the stocktweets collection have the same links or sources
def register_match_link_info(idarray):
    #Create iterable object of all tweets to recognize matching links
    cursor = db.find({"id": {"$in": idarray}})
    #Just regex for https links
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"    

    #reset existing collections
    for i, id in enumerate(idarray):
        document_name = "Shared Link: "+ id
        mng_db[document_name].drop()

    #iterate through queried cursor object and run regex to create link array, then match to other entries in query
    for i, record in enumerate(cursor):
        document_name = "Shared Link: "+ record['id']
        url = re.findall(regex, record['text'])       
        string_array = [x[0] for x in url]
        print(string_array)
        #match links and return
        new_cursor = db.find({"text": {"$in": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}})
        new_doc = mng_db[document_name]
        #Create new collection and insert for each matching record
        for i, new_record in enumerate(new_cursor):
            print(new_record)
            new_doc.insert_one(new_record)


#iterate through tweets cursor, send fields to api using query of timestamp, if volatility above add to new collection. Essentially splits the table based on external variables.
def split_above_volatility(split_value):
    #iterate through tweet, if volatility above add to new collection
    start = input("Enter start of call(Enter main for main_influencers): ")
    end = ""
    add_string = ""
    #Basic setup so that not every tweet needs to iterated on for demo
    if start == "main":
        cursor = db.find({ 'source': { "$in": main_influencers} })
        start = 0
        end = len(main_influencers)
        add_string = "Main: "
    else:
        end = input("Enter end of call: ")
        cursor = db.find()
    mng_db[add_string + "Volatility above " + str(split_value)].drop()

    #iterate over cursor query object and return the fields of individual records. Use fields with yfinance api to get history data and construct volatility
    for i, record in enumerate(cursor[int(start):int(end)]):
        print(record['symbols'])
        print(i)
        tickerSymbol = record['symbols']
        tickerData = yf.Ticker(tickerSymbol)
        time = record['timestamp']

        #financial data over month around tweets, can parse time if needed
        tickerDf = tickerData.history(period='1d', start='2018-6-15', end='2018-7-15')

        open_array = tickerDf._get_column_array(0)
        close_array = tickerDf._get_column_array(3)
        vol = -1

        #If there was available financial data, create new collection and insert 
        if len(close_array) > 0:
            vol = close_array[-1] / open_array[0]
            print(vol)
            if vol > split_value:
                document_name = add_string + "Volatility above " + str(split_value)
                new_doc = mng_db[document_name]
                new_doc.insert_one(record)

#Function to determine the focus on certain companies by important(verified) influencers
def assign_influencer_ratio():
    string_array = ["RT"]
    #return iterable query objects based upon if they are not retweets and they are either verified or not verified
    cursor_verified = db.find({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "True"})
    verified_count = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "True"})
    cursor_unverified = db.find({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "False"})
    unverified_count = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "False"})
    print(f"{verified_count}\n")
    print(f"{unverified_count}\n")

    #Create collection and basic input setup
    new_doc = mng_db["Tweet ratio"]
    new_doc.drop()
    v_start = input("Enter start of call(For verified): ")
    v_end = input("Enter end of call(For verified, enter all for all records): ")

    if v_end == "all":
        v_end = verified_count

    u_start = input("Enter start of call(For UNverified]): ")
    u_end = input("Enter end of call(For UNverified, enter all for all records): ")

    if u_end == "all":
        u_end = unverified_count

    #iterate over cursor query object and use next calls to construct volatility from external data
    for i, record in enumerate(cursor_verified[int(v_start): int(v_end)]):
        verified_count_for_symbol = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "True", "symbols": record['symbols']})
        unverified_count_for_symbol = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "False", "symbols": record['symbols']})

        #If there are no unverified tweets, then assume that there is 1 to create ratio
        if unverified_count_for_symbol == 0:
            unverified_count_for_symbol = 1     
        new_doc.insert_one({"source": record["source"], record["symbols"]: str(verified_count_for_symbol/unverified_count_for_symbol), "initially_verified": "True"})   
        print(record['symbols'] + str(i))

    #iterate over cursor query object and use next calls to construct volatility from external data
    for i, record in enumerate(cursor_unverified[int(u_start): int(u_end)]):
        verified_count_for_symbol = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "True", "symbols": record['symbols']})
        unverified_count_for_symbol = db.count({"text": {"$nin": 
                    [re.compile(r'(?:{})'.format('|'.join(map(re.escape, string_array))))
                    ]}, "verified": "False", "symbols": record['symbols']})
        
        #If there are no unverified tweets, then assume that there is 1 to create ratio
        if unverified_count_for_symbol == 0:
            unverified_count_for_symbol = 1     
        new_doc.insert_one({"source": record["source"], record["symbols"]: str(verified_count_for_symbol/unverified_count_for_symbol), "initially_verified": "False"})   
        print(record['symbols'] + str(i))

if __name__ == '__main__':
    #basic setup
    mongo_client=MongoClient('localhost', 27017)

    mng_db=mongo_client['project3']
    db = mng_db['stocktweets']
    
    #Running switch for function choice
    while(True):
        print("1. Reset database")
        print("2. Split above volatility ")
        print("3. Register and match link info ")
        print("4. Assign tweet ratio ")
        print("0. Exit")
        val = int(input(""))
        if val == 1:
            db = reset_table()
            continue
        elif val == 2:
            split_num = float(input("Enter split decimal: "))
            split_above_volatility(split_num)
            continue
        elif val == 3:
            idarray = []

            #loop to choose mutliple id's to match links with
            while(True):
                id = input("Enter id(Enter exit to skip): ")
                if id == "exit":
                    break
                idarray.append(id)
            if len(idarray) > 0:
                register_match_link_info(idarray)
            continue
        elif val == 4:
            assign_influencer_ratio()
            continue
        elif val == 0:
            break