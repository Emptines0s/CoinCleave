from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ConnectForm,\
    CreateBotForm
from app.tasks import ping_connection, run_bot, send_password_reset_email, send_new_ip_alert_email
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Connect, Bot, Strategy, Subscription, Activity
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
from sqlalchemy import and_, or_


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        activity = Activity(user_id=current_user.id, last_time=datetime.utcnow(), last_ip=request.remote_addr)
        db.session.add(activity)
        db.session.commit()
        if user.settings.ip_alert is True:
            send_new_ip_alert_email.delay(user.email, activity.id)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    if request.method == 'POST':
        return redirect(url_for('reset_password_request'))
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/admin')
@login_required
def admin():
    if current_user.role == 'admin':
        return render_template('admin.html', title='Admin')
    else:
        return redirect(url_for('index'))


@app.route('/faq/<target>')
def faq(target):
    return render_template('faq.html', title='Register', target=target)


@app.route('/subscription', methods=['GET', 'POST'])
@login_required
def subscription():
    subscriptions = Subscription.query.filter(
        and_(Subscription.user_id == current_user.id,
             or_(Subscription.status == 'active', Subscription.status == 'waiting'))).all()
    subscription_time = timedelta()
    for row in subscriptions:
        subscription_time += row.time
    all_purchase = Subscription.query.filter_by(user_id=current_user.id)
    return render_template('subscription.html',
                           title='Subscription',
                           subscription_time=subscription_time,
                           all_purchase=all_purchase)


@app.route('/buy_subscription', methods=['POST'])
def buy_subscription():
    active_subscription = Subscription.query.filter(
        and_(Subscription.user_id == current_user.id, Subscription.status == 'active')).first()
    if active_subscription is not None:
        current_status = 'waiting'
    else:
        current_status = 'active'
    new_subscription = Subscription(user_id=current_user.id,
                                    status=current_status,
                                    name=request.form.get('subscription_name'),
                                    time=timedelta(days=int(request.form.get('subscription_time'))))
    db.session.add(new_subscription)
    db.session.commit()
    return 'Success', 200


@app.route('/bots', methods=['GET', 'POST'])
@login_required
def bots():
    bot_list = current_user.bots
    return render_template('bots.html',
                           title='Bots',
                           bot_list=bot_list)


@app.route('/delete_bot', methods=['POST'])
def delete_bot():
    if request.form.get('bot_id') != 'None':
        bot = Bot.query.get(request.form.get('bot_id'))
        if bot.state == 'disabled':
            db.session.delete(bot)
            db.session.commit()
            return {'bot_id': str(request.form.get('bot_id'))}
    return {'bot_id': 'None'}


@app.route('/get_bot_data', methods=['POST'])
def get_bot_data():
    bot = Bot.query.get(request.form.get('bot_id'))
    bot_strategy = Strategy.query.get(bot.strategy_id)
    bot_trades = []
    for row in bot.trades:
        bot_trades.append([row.datetime, row.ticker, row.type, row.price, row.quantity])
    return {'strategy_name': bot_strategy.name,
            'strategy_description': bot_strategy.description,
            'bot_trades': bot_trades}


@app.route('/start_bot', methods=['POST'])
def start_bot():
    if request.form.get('bot_id') != 'None':
        running_bots_number = Bot.query.filter(
            and_(Bot.user_id == current_user.id,
                 or_(Bot.state == 'active', Bot.state == 'waiting'))).count()
        if running_bots_number < 10:
            run_bot.delay(request.form.get('bot_id'))
            return {'bot_id': str(request.form.get('bot_id'))}
    return {'bot_id': 'None'}


@app.route('/soft_stop_bot', methods=['POST'])
def soft_stop_bot():
    if request.form.get('bot_id') != 'None':
        bot = Bot.query.get(request.form.get('bot_id'))
        if bot.state == 'active':
            bot.state = 'waiting'
            db.session.commit()
            return {'bot_id': str(request.form.get('bot_id'))}
    return {'bot_id': 'None'}


@app.route('/hard_stop_bot', methods=['POST'])
def hard_stop_bot():
    if request.form.get('bot_id') != 'None':
        bot = Bot.query.get(request.form.get('bot_id'))
        if bot.state == 'active' or bot.state == 'waiting':
            bot.state = 'stop'
            db.session.commit()
            return {'bot_id': str(request.form.get('bot_id'))}
    return {'bot_id': 'None'}


@app.route('/create_bot', methods=['GET', 'POST'])
@login_required
def create_bot():
    form = CreateBotForm(connections=current_user.connections)
    if form.validate_on_submit():
        if len(current_user.bots) < 50:
            bot = Bot(user_id=current_user.id,
                      connect_id=Connect.query.filter_by(api_key=form.connect.data).first().id,
                      strategy_id=Strategy.query.filter_by(name=form.strategy.data).first().id,
                      ticker=form.ticker.data.upper(),
                      deposit=form.deposit.data)
            db.session.add(bot)
            db.session.commit()
            flash('Congratulations, bot add!')
        else:
            flash('Bots limit: 50!')
        return redirect(url_for('bots'))
    return render_template('create_bot.html', title='Create Bot', form=form)


@app.route('/get_connect_info', methods=['POST'])
def get_connect_info():
    if request.form.get('connect_api') != '':
        info = db.session.query(Connect.exchange).filter(
            Connect.api_key == request.form.get('connect_api')).scalar()
    else:
        info = ''
    return {'info': info}


@app.route('/get_strategy_info', methods=['POST'])
def get_strategy_info():
    if request.form.get('strategy_name') != '':
        info = db.session.query(Strategy.description).filter(
            Strategy.name == request.form.get('strategy_name')).scalar()
    else:
        info = ''
    return {'info': info}


@app.route('/connections', methods=['GET', 'POST'])
@login_required
def connections():
    connect_list = current_user.connections
    form = ConnectForm()
    if form.validate_on_submit():
        connect = Connect(user_id=current_user.id,
                          exchange=form.exchange.data,
                          api_key=form.api_key.data,
                          secret_key=form.secret_key.data)
        db.session.add(connect)
        db.session.commit()
        flash('Congratulations, connections add!')
        return redirect(url_for('connections'))
    return render_template('connections.html',
                           title='Connections',
                           form=form,
                           connect_list=connect_list,
                           server_ip=request.host.split(':')[0])


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    activity_list = current_user.activities
    user_settings = current_user.settings
    return render_template('settings.html', title='security', activity_list=activity_list, user_settings=user_settings)


@app.route('/change_setting', methods=['POST'])
def change_setting():
    if request.form.get('setting_value') == 'true':
        value = True
    else:
        value = False
    setattr(current_user.settings, request.form.get('setting_type'), value)
    db.session.commit()
    return 'Success', 200


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            send_password_reset_email.delay(form.email.data,
                                            url_for('reset_password', token=token, _external=True))
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/delete_connection', methods=['POST'])
def delete_connection():
    connection = Connect.query.get(request.form.get('connection_id'))
    db.session.delete(connection)
    db.session.commit()
    return {'connection_id': str(request.form.get('connection_id'))}


@app.route('/connection_ping', methods=['POST'])
def connection_ping():
    task = ping_connection.delay(request.form.get('connection_id'))
    return {'Location': url_for('connection_status', task_id=task.id),
            'connection_id': str(request.form.get('connection_id'))}


@app.route('/connection_status/', methods=['GET'])
def connection_status():
    task_id = request.args.get('task_id')
    task = ping_connection.AsyncResult(task_id)
    return {'state': task.state, 'result': task.result}


@app.before_request
def before_request():
    pass
