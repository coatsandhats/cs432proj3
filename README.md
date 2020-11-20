# cs432proj3

CS432/532: Final Project Report

Project Title: Financial tweet matching based on source, volatility, and importance ratio

Team Member(s): Lucas Coats

I.PROBLEM/* 
Briefly and clearly describe what problem you have worked on for this project.If you worked on, for example, Tweeter data analysis, define the problem clearly. 

If you did something related to machine learning/AI, describe what kind of queries you support; that is, describe your contributions in terms of database. */
___________________________________________________________________
My problem is taking a comma separated file of financial tweets from 2018 and their focused companies and returning important information on the relationships between the tweets. This project makes this data easily viewable in separate collections.

This information involves the volatility of companies based around the timing of the tweet; if a company does very well in a short period of time, then it is more likely that more of their tweets will be split into another table.
This information also involves what tweets share information or links from other tweets or sources; if a company is smaller yet popular, then it is more likely that more tweets will be in a new collection.
Lastly, the ratio of verified tweets to unverified tweets refer to how popular a specific company is to major influencers vs smaller influencers(This is debatable based on twitter’s verification system in 2018).
_________________________________________________________________



II.SOFTWARE DESIGN ANDIMPLEMENTATION/* Briefly describe how you designed and implemented your software. Describe which No-SQL database and any tools you used. Also, describewhich parts you implemented. */

A.Software Designand NoSQL-Databse and Tools Used
__________________________________________________________________
Python file includes a basic choice interface to choose different queries.

The NOSQL database used was MongoDB with 2 csv files of financial tweets taken from a Kaggle project. The initial setup of collections in mongodb is implemented in my github repo. 

“Project3” database includes initial collection stocktweets, which is a straight conversion of the csv file, and builds and splits new collections based on user input and financial data.

I used MongoD Compass to visualize different collections.

I used yfinance, a closed source module to extend yahoo’s financial data api after it was deprecated. This is only for returning basic stock history.
I used pymongo, a module for interacting with a MongoDB database with the same syntax.
I used re, a stdlib module for basic regex that can be used in conjunction with pymongo calls.

All code in the github is my implementation. Used only basic financial api calls and constructed information myself to ensure performance(Still could be optimized more).
_________________________________________________________________
B.Supported Queries/* Briefly describe the queries you support */
_________________________________________________________________
reset_table():
    This resets the database maindata, converts a maindata.csv file with predefined headers into a new collection.

register_match_link_info(idarray):
    Passing in an array of the indexes of individual tweets, this query filters and creates new collection based on elements of idarray where other records in the stocktweets collection have the same links or sources.
    Uses regex passed into individual calls to the database to return links and compare.
    Uses a cursor object to iterate over matching tweets and then iterates another cursor object to insert into a new collection.
 split_above_volatility(split_value):
    Passing in a split_value, this query iterates through tweets cursor object, sends fields referring to specific companies to yfinance api using query of timestamp, if volatility of the company during that time is above split_value, add to new collection. Essentially splits the table based on external variables.
    This query allows user input to reduce the number of tweets analyzed.
    A new collection is created for every split_value and only includes tweets from companies that existed in the stock market when the tweet was made.

assign_influencer_ratio():
    Query to determine the focus on certain companies by important(verified) influencers and unverified influencers. This is based on the verification standards of twitter during 2018 which is a lot different from 2020.
    This query uses regex to make sure queries are filtered to not be retweets and are either verified or not. Additional direct calls to the database are to count the number of tweets. Instead of user input, these counts can be used to limit the number of tweets analyzed.
    Based upon if the tweet source was verified or not, create new document in collection with the ratio of verified to unverified tweets of the same company.
__________________________________________________________________

III.PROJECT OUTCOMEPlace the GitHub link to your source code below:
__________________________________________________________________
Includes initial csv files directly converted into MongoDb collection.
https://github.com/coatsandhats/cs432proj3
__________________________________________________________________
Provide all references and clearly describe what you have implemented yourself to avoid plagiarism. We will use automated tools that detect plagiarism across online/offline sources.
_________________________________________________________________
Basic PyMongo setup from documentation.
Basic python stdlib modules.
Use of basic yfinance api calls to get historical data for companies.
CSV files from kaggle dataset, with main influencer list.
All else created by myself.
