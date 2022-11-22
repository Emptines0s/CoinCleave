import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:admin@localhost/CoinCleave'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'coin.cleave@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'hwzqjggxrhwuuveu'
    ADMINS = ['coin.cleave@gmail.com']
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'
    RESULT_BACKEND = 'db+postgresql+psycopg2://postgres:admin@localhost/CoinCleave'
