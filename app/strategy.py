from app.models import Candlestick, Trade
from app import db
# import talib as ta
import pandas as pd
from sqlalchemy import and_, func
from app.tasks.task2 import place_order, tessta


class DefaultStrategy:
    @staticmethod
    def calculate(bot):
        # df = DefaultStrategy.create_df(bot)
        # # df['RSI'] = pd.to_numeric(ta.RSI(df['Close'], 14))
        # last_rsi_value = df.iloc[-1]['RSI']
        # last_trade = DefaultStrategy.get_trade(bot)

        print('CALCULATE')
        # tessta.delay(bot.id, 'BUY', bot.deposit)
        # if last_rsi_value <= 100:
        #     if last_trade.type == 'SELL' or not last_trade:
        #         tessta.delay(bot.id, 'BUY', bot.deposit)
        # elif last_rsi_value >= 100:
        #     if last_trade.type == 'BUY':
        #         tessta.delay(bot.id, 'SELL', last_trade.quantity)

    @staticmethod
    def waiting(bot):
        last_trade = DefaultStrategy.get_trade(bot)
        if last_trade.type == 'SELL':
            bot.state = 'disabled'
            db.session.commit()
        elif last_trade.type == 'BUY':
            DefaultStrategy.calculate(bot)

    @staticmethod
    def stop(bot):
        last_trade = DefaultStrategy.get_trade(bot)
        if last_trade.type == 'BUY':
            place_order.delay(bot.id, 'SELL', last_trade.quantity)
        bot.state = 'disabled'
        db.session.commit()

    @staticmethod
    def create_df(bot):
        candlesticks = Candlestick.query.filter(
            and_(Candlestick.strategy_id == bot.strategy_id, Candlestick.symbol == bot.ticker+'USDT')).all()
        data = []
        for row in candlesticks:
            data.append([row.open, row.high, row.low, row.close])
        df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
        return df

    @staticmethod
    def get_trade(bot):
        time = db.session.query(func.max(Trade.datetime)).filter(Trade.bot_id == bot.id).scalar()
        trade = Trade.query.filter_by(datetime=time).first()
        return trade
