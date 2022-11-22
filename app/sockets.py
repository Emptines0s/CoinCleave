from flask_socketio import join_room, leave_room, emit
from app import app, db, socketio
from app.models import User, Connect
from flask_login import current_user


@socketio.on('join')
def my_join(data):
    join_room(data['room'])


@socketio.on('leave')
def my_leave(data):
    leave_room(data['room'])