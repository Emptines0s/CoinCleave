from app.models import Candlestick, Trade
from app import db
import talib as ta
import pandas as pd
from sqlalchemy import and_, func
from app.tasks.task2 import place_order


class DefaultStrategy:
    @staticmethod
    def calculate(bot):
        # Обьявление и проверка осциллятора Чайкина
        last_trade = DefaultStrategy.get_trade(bot)
        df = DefaultStrategy.create_df(bot)
        df['AD'] = ta.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'])
        df = df.astype({'AD': float})
        current_ad = df.iloc[-2]['AD']
        before_current_ad = df.iloc[-3]['AD']
        ad_data_frame = df[df['AD'] > df['AD'].max() / 20]
        ad_data_frame = ad_data_frame.loc[:, 'AD']

        # Проверка пересечения кривой осциллятора нуля
        if current_ad > 0 and before_current_ad < 0:
            for row in df.iloc[-10:-2]['AD']:
                if row < -abs(ad_data_frame.mean()):
                    if last_trade.type == 'SELL' or not last_trade:
                        place_order.delay(bot.id, 'BUY', bot.deposit)
                        break
        elif current_ad < 0 and before_current_ad > 0:
            for row in df.iloc[-10:-2]['AD']:
                if row < abs(ad_data_frame.mean()):
                    if last_trade.type == 'BUY':
                        place_order.delay(bot.id, 'SELL', last_trade.quantity)
                        break

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
            and_(Candlestick.strategy_id == bot.strategy_id, Candlestick.symbol == bot.ticker)).all()
        data = []
        for row in candlesticks:
            data.append([row.high, row.low, row.close, row.volume])
        df = pd.DataFrame(data, columns=['High', 'Low', 'Close', 'Volume'])
        return df

    @staticmethod
    def get_trade(bot):
        time = db.session.query(func.max(Trade.datetime)).filter(Trade.bot_id == bot.id).scalar()
        trade = Trade.query.filter_by(datetime=time).first()
        return trade
