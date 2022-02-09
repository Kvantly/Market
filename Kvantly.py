
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 20:14:47 2020


"""

import streamlit as st
st.set_page_config(layout="wide")
import altair as alt
import quantstats as qs
import seaborn as sns

import yfinance as yf
import datetime 
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
yf.pdr_override()

st.write("""
# Kvantly - Simplistic trend overview
Shown below are certain metric used to get an better overview of the market.
""")

st.sidebar.header('User Input Parameters')

###########
# sidebar #
###########
option = st.sidebar.selectbox('Select one symbol', ( 'SPY', 'QQQ',"GLD",'OBXD.OL','TLT', 'SPLV'))

today = datetime.date.today()
before = today - datetime.timedelta(days=1000)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')
    
    
Fast_sma=st.sidebar.slider(
    'Set fast momentum indicator',min_value=10,max_value =150,value =50, help= 'Set your short term indicator',step=(1))

Slow_sma=st.sidebar.slider(
  'Set slow momentum indicator',min_value=100,max_value =300,value =200, help= 'Set your long term indicator', step=(1))

    
##############
# Stock data #
##############

# Download data

info= yf.Ticker(option)
name = info.info["shortName"]

st.write(f'{option}'+ str('  -  ') +f'{name}')


indy = yf.download(option,start= start_date,end= end_date,)
indy.bfill(inplace  =True)
indy['SMA']         = indy['Adj Close'].rolling(Slow_sma).mean()
indy['SMA']         = indy['Adj Close'].rolling(Slow_sma).mean()
indy[f'{option}']   = (indy['Adj Close']-indy['SMA'])/indy['SMA'] 
indy['pct']         = indy['Adj Close'].pct_change()

st.area_chart(indy[f'{option}'], width=0, height=0, use_container_width=True)

data = yf.download(option,start= start_date,end= end_date, progress=False)
data['SMA Fast'] = data['Adj Close'].rolling(Fast_sma).mean()
data['SMA Slow'] = data['Adj Close'].rolling(Slow_sma).mean()



st.line_chart(data[['Adj Close','SMA Slow','SMA Fast']])


r = pd.DataFrame(index=indy.index)
r['pct']  = indy['pct']
r['month'] =  pd.DatetimeIndex(r.index).month
#r['Month'] =  pd.DatetimeIndex.month_name(r.index)
r['year'] =  pd.DatetimeIndex(r.index).year
#r['year'] = pd.to_datetime(r.index).dt.year

#df['month'] = pd.to_datetime(df['date']).dt.month
#df['year'] = pd.to_datetime(df['date']).dt.year
bjerka = r.groupby(['year','month'],as_index=False,).sum()
bjerka['pct'] = bjerka['pct']*100

stock = indy['pct']
Mon =qs.stats.monthly_returns(stock)*100

ty = Mon.mean(axis=0)
ty = ty.reset_index(drop=False)
ty = ty.round(2)
#ty = ty.rename(columns={'index': 'Month','0':'%' })
ty = ty.set_axis(['Month', '% Pct',], axis=1, inplace=False)

st.write('Monthly returns')
c =alt.Chart(ty).mark_bar().encode(
    x=alt.X('Month', sort=None), y='% Pct',tooltip=['% Pct'], color=alt.value('Green'),)


st.altair_chart(c, use_container_width=True)

#st.write('Monthly returns',Mon['EOY'])


st.write('Yearly returns')
st.bar_chart(Mon['EOY'])


def make_pretty(styler):
    styler.background_gradient(axis=None, vmin=-30, vmax=30, cmap="RdYlGn")
    return styler

Mon = Mon.style.pipe(make_pretty)

if st.sidebar.checkbox("Monthly Heatmap"):
    st.dataframe(Mon,)




ticks = ['SPY','QQQ','GLD','OBXD.OL']
ind = yf.download(ticks,start= start_date,end= end_date,)['Adj Close']

ind.bfill(inplace=True)
ind['SPY_SMA']          = ind['SPY'].rolling(Slow_sma).mean()
ind['GLD_SMA']          = ind['GLD'].rolling(Slow_sma).mean()
ind['QQQ_SMA']          = ind['QQQ'].rolling(Slow_sma).mean()
ind['OBXD.OL_SMA']      = ind['OBXD.OL'].rolling(Slow_sma).mean()
ind['SPY Momentum']     = (ind['SPY']-ind['SPY_SMA'])/ind['SPY_SMA'] 
ind['QQQ Momentum']     = (ind['QQQ']-ind['QQQ_SMA'])/ind['QQQ_SMA']
ind['GLD Momentum']     = (ind['GLD']-ind['GLD_SMA'])/ind['GLD_SMA']  
ind['OBX Momentum']     = (ind['OBXD.OL']-ind['OBXD.OL_SMA'])/ind['OBXD.OL_SMA'] 



st.line_chart(ind[['SPY Momentum','QQQ Momentum','GLD Momentum','OBX Momentum']], width=0, height=0, use_container_width=True)

# Data of recent days
st.write('Recent data')
st.dataframe(ind.tail(50))
