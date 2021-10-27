# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 10:09:02 2021

@author: AndrewL
"""

import pandas as pd
import requests
import time
import json
import numpy as np

from fake_useragent import UserAgent
from requests.exceptions import HTTPError
from io import StringIO

def set_header_ua():
    user_agent = UserAgent()
    return user_agent.random


def monthly_report(year, month):
    print ("monthly_report()")
    # 假如是西元，轉成民國
    if year > 1990:
        year -= 1911
    
    url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
    if year <= 98:
        url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
    
    print(url)

    # 偽瀏覽器
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
    # 下載該年月的網站，並用pandas轉換成 dataframe
    #r = requests.get(url, headers=headers)
    r = requests.get(url)
    r.encoding = 'big5'

    dfs = pd.read_html(StringIO(r.text), encoding='big-5')

    df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
    
    if 'levels' in dir(df.columns):
        df.columns = df.columns.get_level_values(1)
    else:
        df = df[list(range(0,10))]
        column_index = df.index[(df[0] == '公司代號')][0]
        df.columns = df.iloc[column_index]
    
    df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
    df = df[~df['當月營收'].isnull()]
    df = df[df['公司代號'] != '合計']
    
    # 偽停頓
    time.sleep(5)

    return df

#print (monthly_report(110,6))


def time_Mod(timeString):
    #print ("time_Mod()")
    """ 
    "輸入格式: 2021-10-26 08:00:00" >>> 輸出格式: 1635206400
    """
    struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S") # 轉成時間元組
    time_stamp = int(time.mktime(struct_time)) # 轉成時間戳
    return time_stamp 

    """ 
    print (time_Mod("2021-10-22 08:00:00"))
    print (time_Mod("2021-10-26 08:00:00"))
    """

def stock_period_report(stock_code, stock_area, start_time, end_time):
    print ("stock_period_report()")
    """
    print ("stock_code", stock_code)
    print ("stock_area", stock_area)
    print ("start_time", start_time)
    print ("end_time"  , end_time)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code}.{stock_area}?period1={start_time}&period2={end_time}&interval=1d&events=history&=hP2rOschxO0"
    
    # set_header_ua 產生 headers
    headers = {'user-agent': set_header_ua()}
    response = requests.get(url, headers=headers)

    print("response", response)
    print('')
    # 序列化資料回報
    data = json.loads(response.text)
    print("data", data)
    print('')
    
    
    # 把json格式資料放入pandas中
    df = pd.DataFrame(
        data["chart"]["result"][0]["indicators"]["quote"][0],
        index=pd.to_datetime(
            np.array(data["chart"]["result"][0]["timestamp"]) * 1000 * 1000 * 1000
        ),
        columns=["open","high","low","close","volume"]
    )
    
   # print (data)
    # 印出前3行
    print(df[:3])
    """
    #印出前5行
    print(df.head())
    #印出後5行
    print(df.tail())
    """
    
    # 寫成csv
    df.tail().to_csv(f"{stock_code}_最近五天.csv")
    df.to_csv(f"{stock_code}_{start_time}_{end_time}.csv")
    
    print("===finished===")
    
    # 偽停頓
    time.sleep(5)
    return 0

print (stock_period_report(2330, "TW", time_Mod("2021-10-12 13:30:00"), time_Mod("2021-10-26 08:00:00")))
    

