from API.bithumbapi import bithumbapi
import time
import math
import sys
from API.function import *

nowhour = getNowHour()

apikey = 'c421fe46f3ca15625256ee0fbe4adc05'
secret = 'a0aa152439e973935e71f3c1955e971d'

# 변동폭: 높아질수록 거래 빈도가 줄어 보수적 투자
k = 0.5
# 코인 투자 개수
listsize = 5

# 금일 투자할 코인
todaycoin = {}

api = bithumbapi(apikey=apikey, secret=secret)

# 현재 가지고 있는 코인 구하기
nowcoin = api.getmywallet(code='ALL')

# 현재 가지고 있는 코인 전부 팔기(0시)
if nowhour == 0:
    for i in nowcoin:
        # 원화는 제외
        if i.find('krw') >= 0:
            continue

        # 현재 거래 가능한 코인만
        if not i.find('available_') >= 0:
            continue

        # 최소 거래 가능한 수량이 0.0001 이상인 코인들만
        if not float(nowcoin[i]) >= 0.0001:
            continue

        units = float(nowcoin[i])
        code = i.replace('available_', '')

        api.marketsellcoin(code=code, money='KRW', units=units)

        # 0.05초 텀을 두기
        time.sleep(0.05)


time.sleep(1)
        
todayprice = api.getmywallet(code='ALL')
todayprice = math.floor(float(todayprice['available_krw']))

# 전체 코인 구하기
totalcoin = api.getcurrentprice(code='ALL')

# 날짜 항목은 제외
totalcoin.pop('date')

# 최근 거래량 역순 정렬
totalcode = sorted(totalcoin, key=lambda x: float(totalcoin[x]['acc_trade_value_24H']), reverse=True)
totalcode = totalcode[:listsize]

for code in totalcode:
    coindata = api.getohlcprice(code=code)

    # if len(coindata) <= 20:
    #    continue

    # print(code)
    # print(coindata)

    todaycoin[code] = {
        'todayopen': coindata.iloc[-1]['open']
        , 'k': k
        , 'targetprice': get_target_price(coindata, k)
        , 'nowbuying': False
    }

    time.sleep(0.2)

for i in todaycoin:
    todaycoin[i]['howmuch'] = math.floor(todayprice/len(todaycoin))
    

while True:
    try:
        if len(todaycoin) == 0:
            break

        for code in todaycoin:
            # 현재 코인가격 구하기
            coinprice = api.getcurrentprice(code=code)
            
            # print(code)
            # print(todaycoin[code]['targetprice'])
            # print(coinprice['closing_price'])
            
            # 이미 구매중이면
            if todaycoin[code]['nowbuying'] is True:
                # 현재 코인가격이 5% 손해나면 팔기
                if todaycoin[code]['buymoney'] * 0.95 >= float(coinprice['closing_price']):
                    api.marketsellcoin(code=code, money='KRW', units=todaycoin[code]['units'])
                    
                    todaycoin.pop(code)
            else:
                # 현재 코인 가격이 목표가 이상이면 구입
                if todaycoin[code]['targetprice'] <= float(coinprice['closing_price']):
                    todaycoin[code]['units'] = api.unitfloor(todaycoin[code]['howmuch'] / float(coinprice['closing_price']))
                    api.marketbuycoin(code=code, money='KRW', price=todaycoin[code]['howmuch'])
                    todaycoin[code]['buymoney'] = float(coinprice['closing_price'])
                    todaycoin[code]['nowbuying'] = True
            
            time.sleep(0.2)

    except Exception as e:
        print(e)




