from app.strategy import DefaultStrategy
from app import db
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from app.models import Bot, Candlestick
import time
from sqlalchemy import and_


class TradeLoopInstance:
    def __init__(self, local_socketio):
        self.ws = SpotWebsocketClient()
        self.active_strategy_instance = []
        self.ws_counter = 0
        self.active_bot_instance = []
        self.creation_time = time.time()
        self.life_time = 10  # 60*60*4
        self.emit_time = 0
        self.strategies = {1: DefaultStrategy}
        self.local_socketio = local_socketio

    def print_state(self):
        print(f'C: {self.ws_counter} | WS: {self.active_strategy_instance} | B: {self.active_bot_instance}')

    def _kline(self, message):
        if 'k' in message:
            for strategy in self.active_strategy_instance:
                if [message.get('k').get('s'), message.get('k').get('i')] == strategy.get('params'):
                    candlesticks = Candlestick.query.filter(
                        and_(Candlestick.strategy_id == strategy.get('strategy_id'),
                             Candlestick.symbol == message.get('k').get('s'))).\
                        order_by(Candlestick.datetime).all()
                    if candlesticks[-1].datetime == message.get('k').get('t'):  # Update candle
                        candlestick = Candlestick(datetime=message.get('k').get('t'),
                                                  open=message.get('k').get('o'),
                                                  high=message.get('k').get('h'),
                                                  low=message.get('k').get('l'),
                                                  close=message.get('k').get('c'),
                                                  volume=message.get('k').get('v'),
                                                  strategy_id=strategy.get('strategy_id'),
                                                  symbol=message.get('k').get('s'))
                        db.session.delete(candlesticks[-1])
                        db.session.add(candlestick)
                        db.session.commit()
                    elif candlesticks[-1].datetime < message.get('k').get('t'):  # Add new candle
                        candlestick = Candlestick(datetime=message.get('k').get('t'),
                                                  open=message.get('k').get('o'),
                                                  high=message.get('k').get('h'),
                                                  low=message.get('k').get('l'),
                                                  close=message.get('k').get('c'),
                                                  volume=message.get('k').get('v'),
                                                  strategy_id=strategy.get('strategy_id'),
                                                  symbol=message.get('k').get('s'))
                        db.session.delete(candlesticks[0])
                        db.session.add(candlestick)
                        db.session.commit()

    def create_strategy_instance(self, strategy, symbol, interval):
        if [symbol, interval] not in [x.get('params') for x in self.active_strategy_instance]:
            self.ws.kline(symbol=symbol.lower()+'usdt',
                          id=self.ws_counter,
                          interval=interval,
                          callback=self._kline)
            self.ws_counter += 1
            self.active_strategy_instance.append({'strategy_id': strategy, 'params': [symbol+'USDT', interval]})

    def run_main_loop(self):
        self.ws.start()
        while True:
            active_bot = Bot.query.filter(Bot.state != 'disabled').all()
            for bot in active_bot:
                if bot.id not in self.active_bot_instance:
                    self.create_strategy_instance(bot.strategy.id, bot.ticker, bot.strategy.interval)
                    for dependence in bot.strategy.dependencies:
                        self.create_strategy_instance(bot.strategy.id, dependence.coin, dependence.interval)
                    self.active_bot_instance.append(bot.id)
                elif bot.state == 'active':
                    self.strategies.get(bot.strategy.id).calculate(bot)
                elif bot.state == 'waiting':
                    self.strategies.get(bot.strategy.id).waiting(bot)
                elif bot.state == 'stop':
                    self.strategies.get(bot.strategy.id).stop(bot)
                # if time.time() - self.creation_time >= self.emit_time:
                #     self.local_socketio.emit('trade', 'ПРИВЕТ, Я :))', room=str(bot.id))
                #     self.emit_time += 2
            if time.time() - self.creation_time >= self.life_time:
                break
        self.ws.close()
