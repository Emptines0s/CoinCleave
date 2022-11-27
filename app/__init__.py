from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
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


from app import routes, models, errors, sockets
