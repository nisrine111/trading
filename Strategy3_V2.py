from AlgorithmImports import *
from collections import deque


class startegy3(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.SetCash(100000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
       
        self.sma = CustomSimpleMovingAverage("simple moving average customized", 30)
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily)

    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return
        history = self.History(self.spy, timedelta(261), Resolution.Daily)
        high = max(history["high"])
        low = min(history["low"])
        price = self.Securities[self.spy].Price
       
        if price * 1.05 >= high and price > self.sma.Current.Value:
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)

        elif price * 0.9 < low and price < self.sma.Current.Value:
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1)  

        else:
            self.Liquidate()

        self.Plot("Benchmark", "52 weeks high", high)
        self.Plot("Benchmark", "52 weeks low", low)
        self.Plot("Benchmark", "high area", high * 1.05)
        self.Plot("Benchmark", "low area", low * 0.9)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)


class CustomSimpleMovingAverage(PythonIndicator):
    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)

    def Update(self, input):
        self.queue.appendleft(input.Close)
        count = len(self.queue)
        self.Time = input.EndTime

        self.Value = sum(self.queue) / count
        return count == self.queue.maxlen
