# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 13:24:19 2022

@author: win 8.1
"""

from re import I
import requests
from bs4 import BeautifulSoup
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from time import sleep
#from google.auth.transport import requests
#import google.auth.transport.requests

def get_data():

 
    URL = "https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics"
    r = requests.get(URL)

    soup = BeautifulSoup(r.content, 'html5lib')

    upiStats = [] 

    table = soup.find('table', attrs = {'class':'table table-bordered'})
    
    for row in table.findAll('tr'):
        arr = []
        for data in row.findAll('td'):
            if('%' in data.contents[0]):
                data.contents[0] = float(data.contents[0].rstrip("%"))
            arr.append(data.contents[0])
        upiStats.append(arr)

    df = pd.DataFrame(upiStats[2:], columns =['Serial Number', 'Bank Name', 'Total Volume (In Million)', 'Approved %','BD %','TD %','Total Debit Reversal Count (In Mn)', 'Debit Reversal Access %']) 
    df[["Serial Number","BD %","Total Debit Reversal Count (In Mn)","Debit Reversal Access %"]] =df[["Serial Number","BD %","Total Debit Reversal Count (In Mn)","Debit Reversal Access %"]].apply(pd.to_numeric)
    tempArr = []
    for i in df['Total Volume (In Million)'] :    
        if(',' in i):
            for j in range(len(i)):
                if(i[j] == ','):
                    i = i[:j]+i[j+1:]
                    tempArr.append(float(i))
                    break
        else:
            tempArr.append(float(i))
            
    df['Total Volume (In Million)'] = np.array(tempArr)
    return df
 
def correct_encoding(dictionary):
    """Correct the encoding of python dictionaries so they can be encoded to cloud db
    inputs
    -------
    dictionary : dictionary instance to add as document
    output
    -------
    new : new dictionary with corrected encodings"""

    new = {}
    for key1, val1 in dictionary.items():
        # Nested dictionaries
        if isinstance(val1, dict):
            val1 = correct_encoding(val1)

        if isinstance(val1, np.bool_):
            val1 = bool(val1)

        if isinstance(val1, np.int64) or isinstance(val1, np.int32):
            val1 = int(val1)

        if isinstance(val1, np.float64) or isinstance(val1, np.float32):
            val1 = float(val1)

        new[key1] = val1

    return new

def post_data(data_dict, api_endpoint):
    for serial in range(len(data_dict)):
        r = requests.post(url = api_endpoint + "/add", json = data_dict[serial])
        pastebinurl = r.text
        print(pastebinurl)

    print("data posted")


def delete_collection(api_endpoint):
    r = requests.delete(url = api_endpoint + "/delete")
    print("data deleted")

def update_db():
    df = get_data()

    data_dict = df.to_dict("records")
    for i in range(len(data_dict)):
        # data_dict[i]['id'] = str(i)
        data_dict[i] = correct_encoding(data_dict[i])

    api_endpoint = "http://127.0.0.1:5000"

    delete_collection(api_endpoint= api_endpoint)
    post_data(data_dict= data_dict, api_endpoint= api_endpoint)

# df = get_data()
# data_dict = df.to_dict("records")

# for i in range(len(data_dict)):
 
#     data_dict[i]['id'] = str(i)
#     #print(data_dict[i])
#     data_dict[i] = correct_encoding(dict(data_dict[i]))
       

# cred = credentials.Certificate('upidata-f23a4-firebase-adminsdk-fxqed-e1e9866762.json')
# firebase_admin.initialize_app(cred, {'databaseURL': 'https://upidata.firebaseio.com/'})

# db = firestore.client()
# doc_ref = db.collection(u'applications')

# # Import data
# # tmp = df.to_dict(orient='records')
# list(map(lambda x: doc_ref.add(x), data_dict))

# if __name__ == "__main__":

    while True:

        update_db()
        print("updated db")
        sleep(86400)