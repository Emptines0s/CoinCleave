from binance.spot import Spot
from app import db
from app.models import Trade, Bot
from app.tasks.celery_conf import celery


@celery.task(name='core.place_order')
def place_order(bot_id, side, quantity):
    bot = Bot.query.get(bot_id)
    client = Spot(key=bot.connect.api_key, secret=bot.connect.secret_key)
    if side == 'BUY':
        order = client.new_order(symbol=bot.ticker,
                                 side=side,
                                 type='MARKET',
                                 quoteOrderQty=quantity)
    elif side == 'SELL':
        order = client.new_order(symbol=bot,
                                 side=bot,
                                 type=bot,
                                 quantity=quantity)
    trade = Trade(bot_id=bot.id,
                  ticker=bot.ticker,
                  type=side,
                  price=order.get('price'),
                  quantity=order.get('origQty'),
                  order_id=order.get('orderId'),
                  datetime=order.get('transactTime'))
    db.session.add(trade)
    db.session.commit()
    return 'OrderPlaced'


@celery.task(name='core.tessta')
def tessta(bot_id, side, quantity):
    print('ORDER PLASEDDD1!!')
    print(side)
    return 'ORDER PLASEDDD1!!'
