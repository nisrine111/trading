from AlgorithmImports import *


class traillingStopLoss(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2017, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.ibm = self.AddEquity("IBM", Resolution.Hour).Symbol
        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryTime = datetime.min
        self.stopMarketOrderFill = datetime.min
        self.highestPrice = 0

    def OnData(self, data):  # triggered every time data is sent
        # 30 days after last exit
        if (self.Time - self.stopMarketOrderFill).days < 30:
            return

        price = self.Securities[self.ibm].Price

        # send entry limit order if there are no pending orders
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(
            self.ibm
        ):
            quantity = self.CalculateOrderQuantity(self.ibm, 0.9)
            # limit oder to use 90% of our portfolio to buy share of IBM at limit price
            self.entryTicket = self.LimitOrder(self.ibm, quantity, price, "Entry Order")
            self.entryTime = self.Time

        # if not filled in 1 day move the limit price

        if (
            self.Time - self.entryTime
        ).days > 1 and self.entryTicket.Status != OrderStatus.Filled:
            modifier = UpdateOrderFields()
            modifier.LimitPrice = price
            self.entryTicket.update(modifier)

        # move up trailing stop price
        # requires stop market order ticket

        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            if price > self.highestPrice:
                self.highestPrice = price
                modifier = UpdateOrderFields()
                modifier.StopPrice = price * 0.95
                self.stopMarketTicket.update(modifier)
                self.Debug(f"the highest price is   {self.highestPrice}")

    def onOrderEvent(self, orderEvent):
        if self.entryTicket.Status != OrderStatus.Filled:
            return

        # send stop loss order if limit order is filled
        if (
            orderEvent.OrderId == self.entryTicket.OrderId
            and self.entryTicket is not None
        ):
            self.stopMarketTicket = self.StopMarketOrder(
                self.ibm,
                -self.entryTicket.Quantity,
                0.95 * self.entryTicket.AverageFillPrice,
            )

        # save fill time of stop loss order
        if (
            self.stopMarketTicket is not None
            and self.stopMarketTicket.OrderId == orderEvent.OrderId
        ):
            self.stopMarketOrderFill = self.Time
            self.highestPrice = 0
