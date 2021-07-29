import pandas_datareader.data as web


def datapull(Stock):
    try:
        df = (web.DataReader(Stock, 'yahoo'))
        return df
    except Exception as e:
        print('Main Loop' + str(e))


def relativeStrengthIndex(prices, n):
    RSI = []
    m = len(prices)
    avgGain = 0
    avgLoss = 0

    i = 0
    while i < 14:
        change = prices[i+1] - prices[i]
        if change >= 0:
            avgGain = change + avgGain
        else:
            avgLoss = avgLoss - change
        i += 1

    avgGain = avgGain/n
    avgLoss = avgLoss/n

    t = 14

    while t < m:
        smoothedrs = avgGain/avgLoss
        RSI.append((100 - 100 / (1+smoothedrs)))
        if t < m-1:
            change = prices[t+1] - prices[t]
        if change >= 0:
            avgGain = (avgGain * 13 + change) / n
            avgLoss = (avgLoss * 13) / n
        else:
            avgGain = (avgGain * 13) / n
            avgLoss = (avgLoss * 13 - change) / n
        t += 1

    return RSI

def exponentialMovingAverage(prices, n):
        m = len(prices)
        a = 2/(n+1)
        EMA = []
        EMA.append(prices[0])
        i = 1
        while i < m:
            EMA.append((a * prices[i]) + ((1 - a) * EMA[i - 1]))
            i += 1
        return EMA

def rsi(price, n=14):
    print(price)
    prices = price['Close']
    print(prices)
    rsi = relativeStrengthIndex(prices, n)
    current_rsi = rsi.pop()
    print("RSI(14): " + str(current_rsi))

    ema56 = exponentialMovingAverage(prices, 56)
    current_56 = ema56.pop()
    print("EMA(56): " + str(current_56))

Stock = 'AAPL'
df = datapull(Stock)
rsi(df)
