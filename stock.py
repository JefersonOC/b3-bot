import asyncio
import json
import time
import csv
import os
from datetime import datetime, date

from typing import Dict
from typing import Optional

from dividend import Dividend

import aiohttp
import calendar


def auto_updating_property(func):
    """Decorator which create a property that automaticaly updates itself."""

    def _wrapped(self: 'Stock'):
        self._update()
        return func(self)

    return property(_wrapped)


class StockNotFound(Exception):
    """Exception used when the stock doesn't exist in google-finance database."""
    pass


class Stock:
    """This class is a single stock representation. It use google-finance as it's source of information. Also, it was
     built in a lazily manner, fetching information from Google's API only when necessary."""

    def __init__(self, code: str, quantity: int = 0, initial_price: float = 0, *, max_cache_time: int = 60, dividends: Optional[Dict[str, Dividend]] = None):
        if dividends is None:
            dividends = dict()

        self.code = code.upper()
        self.type = ''
        self.quantity = int(quantity)
        self.last_update: float = 0.0
        self.avg_price = float(initial_price)
        self.max_cache_time = max_cache_time

        self._description = None
        self._price = None
        self._change = None
        self._minPriceInYear: float = 0.0
        self._maxPriceInYear: float = 0.0
        self._returnOnEquity: float = 0.0
        self._earningsPerShare: float = 0.0
        self._netMargin: float = 0.0

        self.dividends = dividends

    @property
    def value(self) -> float:
        """Value of all stocks."""
        return self.quantity * self.price

    @property
    def score(self) -> float:
        """Score os Stock."""
        score: float = 0.0

        """ ROE """
        if self.return_on_equity >= 20:
            score += 5
        elif self.return_on_equity >= 10:
            score += 3
        elif self.return_on_equity < 10:
            score += -3

        """ LPA """
        if self.earnings_per_share >= 0.5:
            score += 5
        elif self.earnings_per_share < 0.5:
            score += -5

        """ ML """
        if self.net_margin >= 30:
            score += 5
        elif self.net_margin >= 10:
            score += 3
        elif self.net_margin <= 1:
            score += -3
        elif self.net_margin < 10:
            score += -1

        """ PM """
        avgPriceYear = float((self.minPriceInYear + self.maxPriceInYear) / 2)
        if self.price < avgPriceYear:
            score += 5
        elif self.price > (avgPriceYear + self.percentage(80, avgPriceYear)):
            score += -5
        elif self.price > (avgPriceYear + self.percentage(60, avgPriceYear)):
            score += -3
        elif self.price < (avgPriceYear + self.percentage(30, avgPriceYear)):
            score += 3

        return score / 4

    @auto_updating_property
    def price(self) -> float:
        """Stock actual price."""
        return self._price

    @auto_updating_property
    def change(self) -> float:
        """Stock change in percentage for the day."""
        return self._change

    @auto_updating_property
    def minPriceInYear(self) -> float:
        return self._minPriceInYear

    @auto_updating_property
    def maxPriceInYear(self) -> float:
        return self._maxPriceInYear

    @auto_updating_property
    def description(self) -> str:
        return self._description

    @auto_updating_property
    def is_valid(self) -> bool:
        """Return true if the stock exist, false otherwise"""
        return self._is_valid

    @auto_updating_property
    def return_on_equity(self) -> float:
        try:
            return self._returnOnEquity
        except (AttributeError):
            return 0.0

    @auto_updating_property
    def earnings_per_share(self) -> float:
        try:
            return self._earningsPerShare
        except (AttributeError):
            return 0.0

    @auto_updating_property
    def net_margin(self) -> float:
        try:
            return self._netMargin
        except (AttributeError):
            return 0.0

    async def update_task(self):
        """Fetch asynchronously all the information from the stock."""
        if time.time() - self.last_update < self.max_cache_time:
            return

        url = f'https://mfinance.com.br/api/v1/stocks/indicators/{self.code}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rsp:
                if rsp.status == 200:
                    text = await rsp.text()
                    self._is_valid = True
                    # Decode the json, we remove some heading and trailing characters
                    fin_data = json.loads(text)

                    self._returnOnEquity = float(
                        fin_data['returnOnEquity']['value'])
                    self._earningsPerShare = float(
                        fin_data['earningsPerShare']['value'])
                    self._netMargin = float(fin_data['netMargin']['value'])

        url = f'https://mfinance.com.br/api/v1/stocks/{self.code}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rsp:
                if rsp.status == 200:
                    text = await rsp.text()
                    self._is_valid = True
                    # Decode the json, we remove some heading and trailing characters
                    fin_data = json.loads(text)

                    self._price = float(fin_data['lastPrice'])
                    self._change = float(fin_data['change'])
                    self._minPriceInYear = float(fin_data['lastYearLow'])
                    self._maxPriceInYear = float(fin_data['lastYearHigh'])
                    self._description = fin_data['name']
                    self.type = 'stock'

                    self.last_update = time.time()
                elif rsp.status == 404:
                    url = f'https://mfinance.com.br/api/v1/fiis/{self.code}'
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as rsp:
                            if rsp.status == 200:
                                text = await rsp.text()
                                self._is_valid = True
                                # Decode the json, we remove some heading and trailing characters
                                fin_data = json.loads(text)

                                self._price = float(fin_data['lastPrice'])
                                self._change = float(fin_data['change'])
                                self._minPriceInYear = float(
                                    fin_data['lastYearLow'])
                                self._maxPriceInYear = float(
                                    fin_data['lastYearHigh'])
                                self._description = 'FII - ' + fin_data['name']
                                self.type = 'fii'

                                self.last_update = time.time()
                            else:
                                self._is_valid = False
                else:
                    self._is_valid = False

    async def update_task_dividends(self):
        """Fetch all the information from the stock."""
        if time.time() - self.last_update < self.max_cache_time:
            return

        dividends = []
        '''
        url = f'https://mfinance.com.br/api/v1/stocks/dividends/{self.code}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rsp:
                if rsp.status == 200:
                    text = await rsp.text()
                    # Decode the json, we remove some heading and trailing characters
                    fin_data = json.loads(text)
                    for dividend in fin_data['dividends']:
                        if not dividend['date'].find("2020-") == -1:
                            print(dividend)
                            obj = Dividend(declared_at=dividend['date'].split("T")[0],
                                           ticker=self.code,
                                           value=float(dividend['value']),
                                           type=dividend['type'])
                            dividends.append(obj)
                    self.dividends = dividends
                elif rsp.status == 404:
        '''
        time.sleep(13)
        print('ratelimit 13s')
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={self.code}.SA&apikey=GN8A9DY0OU2QZXLL'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rsp:
                if rsp.status == 200:
                    text = await rsp.text()
                    # Decode the json, we remove some heading and trailing characters
                    fin_data = json.loads(text)

                    year = 2020
                    for month in range(1, 13):  # Month is always 1..12
                        for day in range(1, calendar.monthrange(year, month)[1] + 1):
                            param_year = str(year)
                            param_month = str(month).zfill(2)
                            param_day = str(day).zfill(2)

                            param_last_date = str(
                                param_year) + '-' + param_month + '-' + param_day + ''

                            try:
                                dividend = fin_data['Monthly Adjusted Time Series'][param_last_date]['7. dividend amount']
                                if not dividend == '0.0000':
                                    obj = Dividend(declared_at=param_last_date,
                                                   ticker=self.code,
                                                   value=float(
                                                       dividend.replace(',', '.')),
                                                   type='')
                                    dividends.append(obj)
                            except (KeyError) as error:
                                print(error)
                        self.dividends = dividends

    def percentage(self, percent, whole):
        return (percent * whole) / 100.0

    def _update(self):
        """Drive the update coroutine."""
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.update_task())
        loop.close()

    def __add__(self, other: 'Stock') -> 'Stock':
        """Add the quantity of two stock with the same code. Also, calculate the investment average price."""
        if self.code == other.code and isinstance(other, Stock):
            sum_quantity = self.quantity + other.quantity
            if sum_quantity == 0:
                self.avg_price = 0
            else:
                self.avg_price = ((self.avg_price * self.quantity) +
                                  (other.avg_price * other.quantity)) / sum_quantity

            self.quantity = sum_quantity
            return self
        else:
            raise TypeError(
                f"Você está tentando adicionar ações de empresas diferentes ({self.code} and {other.code})")
