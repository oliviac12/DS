# python
import datetime
import math
import re
import codecs
import csv
import xlrd
import pytz
import json

# data science
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
from scipy import stats
from pandas.io.json import json_normalize

# sql
import sqlalchemy as sql

''' script for writing Share and Exclusive Leads Comparision
    to a table'''

# functions
#------------------------------------
def executeEquateQuery(query, db = 'email'):

    # function for interacting with equate dat
    if db == 'reporting': engine = sql.create_engine('postgresql+psycopg2://gwen:Equategwen1@equate.cyoakzvtoayj.us-east-1.redshift.amazonaws.com:5439/reporting')
    if db == 'email': engine = sql.create_engine('postgresql://equate_super:rnDfc9Zo0@equatepg.cogolo.net:5432/postgres')
    c   = engine.connect()
    trans = c.begin()
    try:
        rows = c.execute(query)
        trans.commit()
        return rows
    except Exception, e:
        print e
        trans.rollback()
        sys.exit()

#------------------------------------
def get_bidding_data(recency):

    #Direct Post
    #Ping Post
    query = ''' select p.master_id, b.buyer_name, p.price, p.request_type, p.response_payload, b.buyer_type, l.state from bidding.pingposts p
                inner join bidding.buyers b
                on p.buyer_id = b.id
                inner join bidding.lead_attributes l
                on l.master_id = p.master_id
                where p.created_ts_dt >= DATEADD(day, %s, GETDATE())
                and extract(dow from p.created_ts_dt) in (1, 2, 3, 4, 5)
                and extract(hour from p.created_ts_dt) in (9,10,11,12,13,14,15,16,17,18,19,20,21)
                and l.lead_type = 'Health' '''    %recency

    d = pd.DataFrame(executeEquateQuery(query, db = 'reporting').fetchall())
    d.columns = ['id','buyer', 'price', 'type', 'payload', 'buyer_type', 'state']
    d = d.set_index(['id'])
    return d

#------------------------------------------------------------------
def rerun_auction(data_auction, legs_max=5):
    # winner bid exclusive

    sorted_auction =  data_auction[data_auction.type == 'Post'].sort_values(['price'], ascending=False)

    if sorted_auction.shape[0] == 0: return 'False'

    win_price = float(sorted_auction.iloc[0].price)
    win_buyer = sorted_auction.iloc[0].buyer


    direct_buyers =  data_auction[(data_auction.buyer_type == 'direct') & (data_auction.type == 'Ping') ].buyer.values
    shared_bids = []

    for b in direct_buyers:
        shared_bids.append((b, win_price/3))


    # get media alpha ping tree
    if 'Media_Alpha' in data_auction.buyer.values:
        ma_parse = {}
        broken = False
        try: ma_data  = data_auction[(data_auction.buyer == 'Media_Alpha')  & (data_auction.type == 'Ping')]['payload'].values[0]
        except: broken = True
        if not broken:
            try: ma_parse = json.loads(ma_data)
            except: ma_parse = {}

        if 'buyers' in ma_parse:

            ma_ping = json_normalize(ma_parse, 'buyers')
            ma_shared = ma_ping[ma_ping.type == 'shared']


            for i,row in ma_shared.iterrows():
                shared_bids.append((row['buyer'], float(row['bid'])))

        shared_bids.sort(key=lambda tup: tup[1], reverse=True)


    top_bids       = shared_bids[:legs_max]

    shared_sum = 0
    for tup in top_bids: shared_sum += tup[1]


    result = {}
    result['exlusive_win_bid'] = win_price
    result['exlusive_winner']  = win_buyer
    result['sum_shared_bid']   = shared_sum
    result['state']            = data_auction['state'].values[0]
    result['num_shared']       = len(top_bids)
    result['master_id']        = data_auction.index.values[0]
    result['shared_buyers']    = [tup[0] for tup in top_bids]

    return result

#--------------------------------------------------------------


def get_autionResult(unique_idx, data):
    # data = get_bidding_data(recency)
    output = []
    for i, idx in enumerate(unique_idx):
        data_auction = data[data.index == idx]
        res = rerun_auction(data_auction)
        if res != 'False': output.append(res)
        df_out = pd.DataFrame(output)
    return df_out


#--------------------------------------------------------------


def run(recency):
    data = get_bidding_data(recency)
    unique_idx = []

    #get unique master id
    for idx in data.index.tolist():
        if idx in unique_idx: continue
        unique_idx.append(idx)

    df_out = get_autionResult(unique_idx, data)
    df_out['best_price'] = df_out.apply(lambda x: x['exlusive_win_bid'] if x['exlusive_win_bid'] >x['sum_shared_bid'] else x['sum_shared_bid'], axis=1)
    engine = sql.create_engine('postgresql://equate_super:rnDfc9Zo0@equatepg.cogolo.net:5432/postgres')
    # if the schema already exists, add table to the scheme, other wise create schema
    # engine.execute(CreateSchema('popsicle'))
    df_out.to_sql('share_lead_14days', engine, schema= 'popsicle', if_exists='replace')
#------------------------------------------------------------y

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='HADDING NTUPLE FILES')
    parser.add_argument('--recency', required = True, type=str, default='', help='schema')
    parsed = parser.parse_args()
    run(parsed.recency)
