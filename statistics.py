import json
import time
from datetime import datetime, date

import requests
import calendar
import pandas as pd


def main():
    """main function"""
    diffSeg = 0.0
    diffTer = 0.0
    diffQua = 0.0
    diffQui = 0.0
    diffSex = 0.0
    num = 0

    json = requests.get(
        "https://mfinance.com.br/api/v1/stocks/historicals/IBOV?months=120")  # 10 YEAR
    json = json.json()
    for stock in json['historicals']:
        date = pd.Timestamp(stock['date'])
        num += 1
        if date.weekday() == 0:
            diffSeg += (float(stock['open'] * -1) + float(stock['close']))
        if date.weekday() == 1:
            diffTer += (float(stock['open'] * -1) + float(stock['close']))
        if date.weekday() == 2:
            diffQua += (float(stock['open'] * -1) + float(stock['close']))
        if date.weekday() == 3:
            diffQui += (float(stock['open'] * -1) + float(stock['close']))
        if date.weekday() == 4:
            diffSex += (float(stock['open'] * -1) + float(stock['close']))

    div = num/5
    print('Seg: ' + str(round(diffSeg/div, 2)))
    print('Ter: ' + str(round(diffTer/div, 2)))
    print('Qua: ' + str(round(diffQua/div, 2)))
    print('Qui: ' + str(round(diffQui/div, 2)))
    print('Sex: ' + str(round(diffSex/div, 2)))


if __name__ == '__main__':
    main()
