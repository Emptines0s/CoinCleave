from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from app.models import User, Strategy, ExchangeTicker, Connect
from app import db


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Изменить пароль')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сохранить')


class ConnectForm(FlaskForm):
    exchange = SelectField('Exchange', choices=['Binance'])
    api_key = StringField('Api Key', validators=[DataRequired()])
    secret_key = StringField('Secret Key', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class CreateBotForm(FlaskForm):
    connect = SelectField('Подключение', validators=[DataRequired()])
    strategy = SelectField('Стратегия', validators=[DataRequired()])
    ticker = StringField('Торговая пара', validators=[DataRequired()])
    deposit = IntegerField('Депозит', validators=[DataRequired(), NumberRange(min=10, max=2147483647)])
    submit = SubmitField('Создать')

    def __init__(self, connections):
        super(CreateBotForm, self).__init__()

        self.connect.choices = [conn.api_key for conn in connections]
        self.strategy.choices = [strats.name for strats in Strategy.query.all()]

    def validate_ticker(self, ticker):
        selected_exchange = Connect.query.filter_by(api_key=self.connect.data).first().exchange
        print(selected_exchange)
        exchange_tickers = db.session.query(ExchangeTicker.ticker).filter(
            ExchangeTicker.exchange == selected_exchange).all()
        if ticker.data not in [ticker[0] for ticker in exchange_tickers]:
            raise ValidationError('Wrong ticker')
