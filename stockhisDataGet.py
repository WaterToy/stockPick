import os
import requests
import json
import csv
import re
import pandas as pd
from time import sleep
from datetime import datetime, timedelta

class stockDataDownload(object):
    def __init__(self):
        # 所有股票代码API
        self.tick_code_api = 'https://api.doctorxiong.club/v1/stock/all'
        # 股票历史交易数据API（网易财经）
        self.tick_his_api = 'http://quotes.money.163.com/service/chddata.html'


    def stock_code_save(self, dirname):
        try:
            if not os.path.exists(dirname):
                print ('文件夹', dirname, '不存在，已重新建立')
                os.makedirs(dirname)

            # 所有股票代码数据存储文件名称
            all_stock_code = 'all_stock_code.csv'
            filepath = os.path.join(dirname, all_stock_code)

            html = requests.get(self.tick_code_api).text
            content = json.loads(html)

            with open (filepath, 'w') as w:
                w.write('StockCode,StockName\n')
                for i in content['data']:
                    t = i[0] + ',' + i[1] + '\n'
                    w.write(t)
            w.close()
            print('已完成所有股票代码下载')

        except IOError as e:
            print ('文件操作失败',e)
        except Exception as e:
            print ('错误 ：',e)

    def tick_his_download(self, stickcode, dirname):
        '''
        stickcode：股票代码
        dirname：数据存储文件夹

        下载指定代码股票从1990.01.01开始的日K数据，或接续现存数据更新数据
        接口采用网易财经接口：'http://quotes.money.163.com/service/chddata.html?code=0601012&start=20120411&end=20210908&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        code: 股票代码
        start/end：开始日期/结束日期
        fields:具体下载的字段
            TCLOSE：当日收盘价
            HIGH：当日最高价
            LOW：当日最低价
            TOPEN：当日开盘价
            LCLOSE：昨日收盘价
            CHG：涨跌额
            PCHG：涨跌幅
            TURNOVER：换手率
            VOTURNOVER：成交量
            VATURNOVER：成交额
            TCAP：总市值
            MCAP：流通市值
        '''
        
        # 股票下载参数
        param = {
            'code': '0'+stickcode[2:],
            'start': '19900101',
            'fields': 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        }
        try:
            if not os.path.exists(dirname):
                print ('文件夹', dirname, '不存在，已重新建立')
                os.makedirs(dirname)
            
            filepath = os.path.join(dirname, stickcode+'.csv')
            # 判断filepath代表的csv文件是否存在，存在则更新数据
            if os.path.exists(filepath):
                # 读取文件内最新一条数据是哪一天的
                tmpdf = pd.read_csv(filepath, encoding='gbk')[['日期']]
                lastDate = tmpdf.sort_values(by='日期').tail(1).values[0][0]
                # 若最新数据不是今天的，则从最新数据的日期之后开始追加写入
                if lastDate < (datetime.now()).strftime('%Y-%m-%d'):
                    param['start'] = (datetime.strptime(lastDate,'%Y-%m-%d')+timedelta(days=1)).strftime('%Y%m%d')
                    response = requests.get(self.tick_his_api, params=param)
                    if response.status_code!=200:
                        print('股票%s数据更新失败，开始下一个任务...'%stickcode)
                        return
                    # print(response.text[61:-2])   去掉首行的列名，尾行换行符
                    with open(filepath, mode='ab+') as w:
                        w.write(r'\n'.encode('gbk'))
                        w.write(response.text[61:-2].encode('gbk',errors='ignore'))
                    w.close()
                    print('股票%s数据已更新至%s...'%(stickcode, datetime.now().strftime('%Y-%m-%d')))
            else:
                # 下载新股数据并存储
                response = requests.get(self.tick_his_api, params=param)
                if response.status_code!=200:
                    print('股票%s下载失败，开始下一个任务...'%stickcode)
                    return
                with open(filepath, mode='ab+') as w:
                    w.write(response.text[:-2].encode('gbk',errors='ignore'))    # 去掉尾行换行符  unix是\r\n 所以2个字符
                w.close()
                print('股票%s数据已完成下载...'%stickcode)
        except IOError as e:
            print ('文件操作失败',e)
        except Exception as e:
            print ('错误 ：',e)

    # 获取当前路径，文件夹，文件
    def get_file_info(self, file_dir):
        for root, dirs, files in os.walk(file_dir):
            # print(root)
            # print(dirs)
            # print(files)
            pass
        return root, dirs, files

sdd = stockDataDownload()
if os.path.exists(r'C:\Users\Chenc'):
    stockhisData_dir = r'C:\Users\Chenc\OneDrive - whut.edu.cn\个人\AutoStock\dataDownload'
    codePath = r'C:\Users\Chenc\Desktop\临时\Development\stockPick'
if os.path.exists(r'C:\Users\19047552'):
    stockhisData_dir = r'C:\Users\19047552\OneDrive - whut.edu.cn\个人\AutoStock\dataDownload'
    codePath = r'D:\个人\Python学习\myspace\stockPick'

sdd.stock_code_save(stockhisData_dir)
stockCodefile = os.path.join(stockhisData_dir, 'all_stock_code.csv')
with open(stockCodefile, mode='r') as r:
    f_csv = csv.reader(r)
    for row in f_csv:
        if row[0]=='StockCode':
            continue
        print('当前目标股票：', row)
        sdd.tick_his_download(stickcode=row[0], dirname=stockhisData_dir)
        sleep(0.3)
r.close()