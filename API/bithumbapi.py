import requests
import time
import math
import base64
import hmac
import hashlib
import urllib.parse
import json
from pandas import DataFrame
import pandas as pd

class bithumbapi:
    apiUrl = 'https://api.bithumb.com'

    def __init__(self, apikey, secret):
        self.apikey = apikey
        self.secret = secret

    # GET 방식
    def requestgetmethod(self, uri, params={}):
        url = self.apiUrl + uri
        result = requests.get(url, params=params)

        if result.status_code == 200:
            return result.text
        else:
            return None

    # secret key 세팅
    def setsecretkey(self, uri, nonce, data):
        key = self.secret.encode('utf-8')

        str_data = urllib.parse.urlencode(data)

        query_string = uri + chr(0) + str_data + chr(0) + nonce
        h = hmac.new(bytes(key), query_string.encode('utf-8'), hashlib.sha512)
        hex_output = h.hexdigest().encode('utf-8')

        return base64.b64encode(hex_output).decode('utf-8')

    # POST 방식
    def requestpostmethod(self, uri, data={}):
        data['endpoint'] = uri

        nonce = str(int(time.time() * 1000))

        headers = {
            'Api-Key': self.apikey.encode('utf-8')
            , 'Api-Sign': self.setsecretkey(uri=uri, nonce=nonce, data=data)
            , 'Api-Nonce': nonce
        }

        url = self.apiUrl + uri
        result = requests.post(url, headers=headers, data=data)

        if result.status_code == 200:
            return json.loads(result.text)
        else:
            return None

    # 소수점 4자리 반올림
    def unitfloor(self, unit):
        return math.floor(unit * 10000) / 10000

    # 코인 현재가 정보 호출
    def getcurrentprice(self, code='BTC', money='KRW'):
        uri = '/public/ticker/{}_{}'.format(code, money)

        data = self.requestgetmethod(uri)
        data = json.loads(data)

        return data['data']

    def getorderbook(self, code='BTC', money='KRW'):
        uri = '/public/orderbook/{}_{}'.format(code, money)
        data = self.requestgetmethod(uri)
        data = json.loads(data)
        return data

    def gettransactionhistory(self, code='BTC', money='KRW'):
        uri = '/public/transaction_history/{}_{}'.format(code, money)
        data = self.requestgetmethod(uri)
        data = json.loads(data)
        return data

    def getohlcprice(self, code='BTC', money='KRW', interval='24h'):
        uri = '/public/candlestick/{}_{}/{}'.format(code, money, interval)
        tmp = self.requestgetmethod(uri)

        data = json.loads(tmp)

        df = DataFrame(data['data'], columns=['datetime', 'open', 'close', 'high', 'low', 'volume'])
        df = df.set_index('datetime')
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.astype(float)
        df.index = pd.to_datetime(df.index, unit='ms', utc=True)
        df.index = df.index.tz_convert('Asia/Seoul')
        if interval == '24h':
            df.index = df.index.strftime('%Y-%m-%d')
        else:
            df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')
        return df

    # 내 정보, 코인거래 데이터 호출
    def getmyinfo(self, code):
        param = {
            'order_currency': code
            , 'payment_currency': 'KRW'
        }

        uri = '/info/account'
        data = self.requestpostmethod(uri, param)
        return data

    # 내 자산 정보 호출
    def getmywallet(self, code='ALL'):
        param = {
            'currency': code
        }

        uri = '/info/balance'
        data = self.requestpostmethod(uri, param)

        if data['status'] == '0000':
            return data['data']
        else:
            return None

    def getmyticker(self, code, money):
        param = {
            'order_currency': code
            , 'payment_currency': money
        }

        uri = '/info/ticker'
        data = self.requestpostmethod(uri, param)
        return data

    def getorderinfo(self, code, money):
        param = {
            'order_currency': code
            , 'payment_currency': money
        }

        uri = '/info/orders'
        data = self.requestpostmethod(uri, param)
        return data

    # 가상화폐 시장가 매수
    def marketbuycoin(self, code, money, price):
        priceInfo = self.getorderbook(code=code, money=money)

        units = self.unitfloor(price / float(priceInfo['data']['asks'][0]['price']))

        if units == 0:
            return None

        param = {
            'order_currency': code
            , 'payment_currency': money
            , 'units': units
        }

        uri = '/trade/market_buy'
        data = self.requestpostmethod(uri, param)
        return data

    # 가상화폐 시장가 매도
    def marketsellcoin(self, code, money, units):
        if units == 0:
            return None

        param = {
            'order_currency': code
            , 'payment_currency': money
            , 'units': self.unitfloor(units)
        }

        uri = '/trade/market_sell'
        data = self.requestpostmethod(uri, param)
        return data

if __name__ == '__main__':
    print('cannot run')