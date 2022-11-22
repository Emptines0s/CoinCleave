from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from celery import Celery
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "Войдите в аккаунт или зарегистрируйтесь"
mail = Mail(app)
socketio = SocketIO(app, message_queue='amqp://guest:guest@localhost:5672//for_socketio')


def make_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])

    celery.conf.task_routes = {
        'core.*': {'queue': 'core'},
        'subsc.*': {'queue': 'subsc'},
        'web.*': {'queue': 'web'}
    }
    celery.conf.beat_schedule = {
        'test-celery': {
            'task': 'check_subscription_time',
            'schedule': 60,
            'options': {'queue': 'subsc'}
        },
        'test-loop': {
            'task': 'trade_main_loop',
            'schedule': 15,
            'options': {'queue': 'core'}
        },
    }
    celery.conf.update()

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


from app import routes, models, errors, sockets
