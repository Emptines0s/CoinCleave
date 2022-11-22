from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from app.models import User, Strategy


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Apply Password Reset')


class ConnectForm(FlaskForm):
    exchange = SelectField('Exchange', choices=['Binance'])
    api_key = StringField('Api Key', validators=[DataRequired()])
    secret_key = StringField('Secret Key', validators=[DataRequired()])
    submit = SubmitField('Add Connection')


class CreateBotForm(FlaskForm):
    connect = SelectField('Connect')
    strategy = SelectField('Strategy')
    ticker = StringField('Ticker', validators=[DataRequired()])
    deposit = IntegerField('Deposit', validators=[DataRequired(), NumberRange(min=10, max=2147483647)])
    submit = SubmitField('Create Bot')

    def __init__(self, connections):
        super(CreateBotForm, self).__init__()

        self.connect.choices = [conn.api_key for conn in connections]
        self.strategy.choices = [strats.name for strats in Strategy.query.all()]

    def validate_ticker(self, ticker):
        if ticker.data not in ['BTC', 'BNB', 'btc']:
            raise ValidationError('Wrong ticker')

