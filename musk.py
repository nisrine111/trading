from nltk.sentiment import SentimentIntensityAnalyzer
from AlgorithmImports import *
class MyAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 11, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100000)
        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol
        self.musktwts = self.AddData(MuskTweets, "MUSKTWTS" , Resolution.Minute).Symbol
        # self.AddData( class_name, ticker to access the class with ,  resolution )
        self.Schedule.On(self.DateRules.EveryDay(self.tsla), self.TimeRules.BeforeMarketClose(self.tsla, 15),self.ExitPosition)

    def OnData(self, data):
        if self.musktwts in data:
            score = data[self.musktwts].Value
            content = data[self.musktwts].Tweet

            if score > 0.5 : 
                self.SetHoldings(self.tsla, 1)
            elif score < -0.5 :
                self.SetHoldings(self.tsla , -1)
            if abs(score) > 0.5:
                self.Log("Score: " + str(score) + ", Tweet: " + content)
            
    def ExitPosition(self):
        return self.Liquidate()
    
class MuskTweets(PythonData):
    # override getsource and reader functions
    sia = SentimentIntensityAnalyzer()

    def GetSource(self, config, date, isLive):
        source = "https://www.dropbox.com/s/ovnsrgg1fou1y0r/MuskTweetsPreProcessed.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config,line, date, isLive):
        
        if not (line.strip() and line[0].isdigit()): # if the line doesn t have any sinificant characters or the first element isn t a digit
            return None
            
        data= line.split(',')
        tweet = MuskTweets()

        try:
            tweet.Symbol =  config.Symbol
            tweet.Time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)
            content = data[1].lower()
            if "tesla" in content or "tsla" in content:
                tweet.Value = self.sia.polarity_scores(content)["compound"]
            else :
                tweet.Value = 0
            tweet["Tweet"] = str(content)

        except ValueError:
            return None

        return tweet


            
    
