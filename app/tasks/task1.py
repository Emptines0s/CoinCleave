import time
from flask_mail import Message
from flask import render_template
from binance.spot import Spot
from binance.error import ClientError, ServerError
from requests.exceptions import ConnectionError
from app import app, mail, db
from app.models import Connect, Subscription, Bot, Candlestick, Activity, ExchangeTicker
from celery.exceptions import SoftTimeLimitExceeded
from datetime import timedelta
from sqlalchemy import and_, func
from app.trade import TradeLoopInstance
from flask_socketio import SocketIO
from app.tasks.celery_conf import celery


@celery.task(name='web.run_bot',  soft_time_limit=8)
def run_bot(bot_id):
    try:
        bot = Bot.query.get(bot_id)
        if bot is None:
            return 'MissingBotError'
        if bot.state == 'active':
            return 'AlreadyActive'
        client = Spot()
        ticker_klines = client.klines(bot.ticker, bot.strategy.interval, limit=bot.strategy.limit)
        last_time = db.session.query(func.max(Candlestick.datetime)).filter(
            and_(Candlestick.strategy_id == bot.strategy.id, Candlestick.symbol == bot.ticker)).scalar()
        if last_time is None:
            last_time = 0
        if abs(time.time() - (last_time / 1000)) > 5:  # Update candlestick if data is outdated
            db.session.query(Candlestick).filter(
                and_(Candlestick.strategy_id == bot.strategy.id, Candlestick.symbol == bot.ticker)).delete()
            for row in ticker_klines:
                candlestick = Candlestick(datetime=row[0],
                                          open=row[1],
                                          high=row[2],
                                          low=row[3],
                                          close=row[4],
                                          volume=row[5],
                                          symbol=bot.ticker)
                bot.strategy.candlesticks.append(candlestick)
        for dependence in bot.strategy.dependencies:
            dependence_klines = client.klines(dependence.coin, dependence.interval, limit=dependence.limit)
            last_time = db.session.query(func.max(Candlestick.datetime)).filter(
                and_(Candlestick.strategy_id == bot.strategy.id, Candlestick.symbol == dependence.coin)).scalar()
            if last_time is None:
                last_time = 0
            if abs(time.time() - (last_time / 1000)) > 5:  # Update candlestick if data is outdated
                db.session.query(Candlestick).filter(
                    and_(Candlestick.strategy_id == bot.strategy.id, Candlestick.symbol == dependence.coin)).delete()
                for row in dependence_klines:
                    candlestick = Candlestick(datetime=row[0],
                                              open=row[1],
                                              high=row[2],
                                              low=row[3],
                                              close=row[4],
                                              volume=row[5],
                                              symbol=dependence.coin)
                    bot.strategy.candlesticks.append(candlestick)
        bot.state = 'active'
        db.session.commit()
        return 'BotStarted'
    except SoftTimeLimitExceeded:
        return 'TimeLimitError'


@celery.task(name='web.ping_connection', soft_time_limit=8)
def ping_connection(connection_id):
    try:
        connect = Connect.query.get(connection_id)
        client = Spot(key=connect.api_key,
                      secret=connect.secret_key)
        client.account()
        return 'Connect'
    except ClientError:
        return 'ClientError'
    except ServerError:
        return 'ServerError'
    except SoftTimeLimitExceeded:
        return 'TimeLimitError'
    except ConnectionError:
        return 'ConnectionError'


@celery.task(name='check_subscription_time')
def check_subscription_time():
    subscriptions = Subscription.query.filter_by(status='active').all()
    for subscription in subscriptions:
        subscription.update_time()
        db.session.commit()
        if subscription.time <= timedelta(seconds=0):
            subscription.status = 'overdue'
            db.session.commit()
            active_subscription = Subscription.query.filter(
                and_(Subscription.user_id == subscription.user_id, Subscription.status == 'waiting')
            ).first()
            if active_subscription is not None:
                active_subscription.status = 'active'
                db.session.commit()
    return 'SubscriptionUpdate'


@celery.task(name='update_exchange_tickers')
def update_exchange_tickers():
    try:
        client = Spot()
        info = client.exchange_info().get('symbols')
        for row in info:
            ticker = ExchangeTicker(exchange='Binance', ticker=row.get('symbol'))
            db.session.add(ticker)
        db.session.commit()
    except ServerError:
        return 'ServerError'
    except ConnectionError:
        return 'ConnectionError'


@celery.task(name='trade_main_loop')
def trade_main_loop():
    local_socketio = SocketIO(message_queue='amqp://guest:guest@localhost:5672//for_socketio')
    instance = TradeLoopInstance(local_socketio)
    instance.run_main_loop()
    return 'CycleStop'


@celery.task(name='web.send_password_reset_email')
def send_password_reset_email(user_email, url):
    msg = Message('Reset password', sender=app.config['ADMINS'][0], recipients=[user_email])
    msg.body = render_template('email/reset_password.txt', user=user_email, url=url)
    msg.html = render_template('email/reset_password.html', user=user_email, url=url)
    mail.send(msg)


@celery.task(name='web.send_new_ip_alert_email')
def send_new_ip_alert_email(user_email, activity_ip):
    activity = Activity.query.get(activity_ip)
    msg = Message('Вход в аккаунт с нового IP', sender=app.config['ADMINS'][0], recipients=[user_email])
    msg.body = render_template('email/login_alert.txt', user=user_email, ip=activity.last_ip, time=activity.last_time)
    msg.html = render_template('email/login_alert.html', user=user_email, ip=activity.last_ip, time=activity.last_time)
    mail.send(msg)
