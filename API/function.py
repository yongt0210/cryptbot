import datetime

# 최적의 k 값 확인
def get_ror(df, k, day):
    df['range'] = df['high'] - df['low']

    df['target'] = df['open'] + df['range'].shift(1) * k
    df['nextopen'] = df['open'].shift(-1)

    df = df.tail(day)

    cond = df['high'] > df['target']

    winrate = df.loc[cond, 'nextopen'] / df.loc[cond, 'target']

    return winrate.cumprod()[-1]

# 코드별 목표가 설정
def get_target_price(df, k):
    yesterday = df.iloc[-2]
    today = df.iloc[-1]

    range = yesterday['high'] - yesterday['low']
    targetprice = today['open'] + range * k

    return targetprice

# 현재 시간 구하기
def getNowHour():
    now = datetime.datetime.now()
    return int(now.strftime('%H'))