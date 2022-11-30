from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime, timedelta
import jwt
from time import time


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='common')
    subscriptions = db.relationship('Subscription', backref='user')
    connections = db.relationship('Connect', backref='user')
    bots = db.relationship('Bot', backref='user')
    settings = db.relationship('Settings', uselist=False, backref='user')
    activities = db.relationship('Activity', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token.encode('utf-8'), app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(user_id)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_alert = db.Column(db.Boolean, default=False)
    subscription_alert = db.Column(db.Boolean, default=True)
    news_alert = db.Column(db.Boolean, default=True)
    bots_report = db.Column(db.Boolean, default=False)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_ip = db.Column(db.String(40))


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(10))
    name = db.Column(db.String(10))
    purchase_time = db.Column(db.DateTime, default=datetime.utcnow)
    time = db.Column(db.Interval)

    def update_time(self):
        if self.time > timedelta():
            self.time -= timedelta(minutes=1)


class Connect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exchange = db.Column(db.String(40))
    api_key = db.Column(db.String(120))
    secret_key = db.Column(db.String(120))
    bots = db.relationship('Bot', backref='connect')


class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    interval = db.Column(db.String(3))
    description = db.Column(db.String(255))
    limit = db.Column(db.Integer)
    bots = db.relationship('Bot', backref='strategy')
    dependencies = db.relationship('Dependence', backref='strategy')
    candlesticks = db.relationship('Candlestick', backref='strategy')


class Dependence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))
    coin = db.Column(db.String(15))
    interval = db.Column(db.String(3))
    limit = db.Column(db.Integer)


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    connect_id = db.Column(db.Integer, db.ForeignKey('connect.id'))
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))
    ticker = db.Column(db.String(15))
    deposit = db.Column(db.Integer)
    pnl = db.Column(db.Float)
    state = db.Column(db.String(15), default='disabled')
    trades = db.relationship('Trade', backref='bot')


class Candlestick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))
    symbol = db.Column(db.String(15))
    datetime = db.Column(db.BigInteger)
    open = db.Column(db.String(20))
    high = db.Column(db.String(20))
    low = db.Column(db.String(20))
    close = db.Column(db.String(20))
    volume = db.Column(db.String(20))


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    order_id = db.Column(db.Integer)
    datetime = db.Column(db.BigInteger)
    ticker = db.Column(db.String(15))
    type = db.Column(db.String(20))
    price = db.Column(db.Float)
    quantity = db.Column(db.Float)


class ExchangeTicker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exchange = db.Column(db.String(15))
    ticker = db.Column(db.String(15))


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
