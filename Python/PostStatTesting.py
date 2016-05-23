#data science
import pandas as pd
from scipy import stats
import scipy as sp
from statsmodels.sandbox.stats.multicomp import multipletests
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu
import numpy as np

# sql
import sqlalchemy as sql

''' script for writing post lead hypothesis testing significant(is certain county's post price significanly higher than the state average)
    to a table'''

# functions
#------------------------------------
def executeEquateQuery(query, db = 'email'):
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

# functions
#------------------------------------
def get_data(startdate, enddate):

    '''get bidding data '''

    media_query = '''
        select p.created_ts_dt, price, buyer_name, p.master_id, county_name, persons_per_household ,income_per_household ,request_type, l.state
        from bidding.pingposts p
        left join bidding.lead_attributes l
        on l.master_id = p.master_id
        left join bidding.buyers b
        on b.id = p.buyer_id
        left join site.zipcodes s
        on s.zip = l.zip
         where p.created_ts_dt > '%s'
         and p.created_ts_dt < '%s'
        AND lead_type = 'Health'
        '''
    query = media_query %  (startdate, enddate)
    data = pd.DataFrame(executeEquateQuery(query, db = 'reporting').fetchall())
    data.columns = ['time', 'price','buyer','master_id','county','persons_per_household', 'income_per_household','request_type','state']
    data['price'] = map(float, data['price'])
    winner = data[(data['request_type'] == 'Post') & (data['price'] > 0)]
    return winner

# functions
#------------------------------------

def get_state(statename, winner, d):

    '''return table with stat significant for each state'''

    if len(winner[winner['state'] == statename]) < 3: return
    #get avarage post price and standard deviation
    state_mean = winner[winner['state'] == statename]['price'].mean()
    state_sd = winner[winner['state'] == statename]['price'].std()

    # get sample tests that have size larger than 20 and avergae post price larger than state mean
    # 20 is to make sure it's ok to perform a hypothesis test
    df = d[(d['state'] == statename) & (d['price']['count'] > 20)&(d['price']['mean'] > state_mean)]

    # If the distribution of all state price is normal, then we can use z test. If not, use a non-paramatric hypothesis testing
    # if the population size is larger than 5000, assume normal, if not, run stats.shapiro to test normality.
    if len(winner[winner['state'] == statename]) < 5000:
        stat, pval = stats.shapiro(winner[winner['state'] == statename]['price'])
        if pval > 0.05:
#             print "it's normal"
            z_test(state_mean, state_sd, df)
        else:
#             print "it's non-normal"
            stat_list = []
            df.apply(lambda row: go_nonpar(row['county'].values[0], row['state'].values[0], stat_list, state_mean, winner), axis=1)
            df["pval"] = stat_list
    else:
#         print "it's normal"
        z_test(state_mean, state_sd, df)
    alpha = 0.05
    df["reject_naive"] = 1*(df["pval"] < alpha)
    try:
        df["reject_bc"] = 1*(df["pval"] < alpha / len(df))
        is_reject, corrected_pvals, _, _ = multipletests(df["pval"], alpha=0.1, method='fdr_bh')
        df["reject_fdr"] = 1*is_reject
        df["pval_fdr"] = corrected_pvals
    except:
        pass

    return df

# functions
#------------------------------------
def go_nonpar(county, state, stat_list, statemean, winner):

    '''non-paramatric test when the distribution is not normal'''


    sample = winner[(winner['county'] == county) & (winner['state'] == state)]['price'].values
    z_statistic, p_value = wilcoxon(sample - statemean)
    stat_list.append(p_value/2)

# functions
#------------------------------------
def z_test(state_mean, state_sd, df):

    '''z-test when the distribution is normal'''



    df['zval'] = (df['price']['mean'] - state_mean) * np.sqrt(df['price']['count'])/ state_sd
    df['pval'] = (1-sp.stats.norm.cdf(df['zval']))

# functions
#------------------------------------
def run(startdate, enddate):
    winner = get_data(startdate, enddate)
    print winner
    d = pd.DataFrame(winner.groupby(['county','state'], as_index=False).agg({'price':['mean','count']}))
    DF = pd.DataFrame()
    all_states = set(winner['state'])
    for state in all_states:
        DF = DF.append(get_state(state, winner, d))
    DF.columns = ['county', 'count', 'mean', 'pval', 'pval_fdr', 'reject_bc',
       'reject_fdr', 'reject_naive', 'state', 'zval']
    engine = sql.create_engine('postgresql://equate_super:rnDfc9Zo0@equatepg.cogolo.net:5432/postgres')
    # if the schema already exists, add table to the scheme, other wise create schema
    # engine.execute(CreateSchema('popsicle'))
    DF.to_sql('BiddingTest', engine, schema= 'popsicle', if_exists='replace')



if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser(description='HADDING NTUPLE FILES')
    # parser.add_argument('--startdate,enddate', required = True, type=str, default='', help='schema')
    # parsed = parser.parse_args()
    run('2016-02-01','2016-03-01')
