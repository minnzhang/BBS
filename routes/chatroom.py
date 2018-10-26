from flask import (
    session,
    redirect,
    url_for,
    render_template,
    request,
    Blueprint
)

from flask_socketio import (
    emit,
    join_room,
    leave_room,
    SocketIO
)

main = Blueprint('chatroom', __name__)

socketio = SocketIO()


@main.route('/')
def index():
    return render_template('/chatroom/index.html')


@main.route('/enter', methods=['POST'])
def enter():
    """
    加入聊天室, name 保存在 session 里面
    """
    name = request.form.get('name')
    if name is not None:
        session['name'] = name
        return redirect(url_for('.chat'))
    else:
        return redirect(url_for('.index'))


@main.route('/chat')
def chat():
    name = session.get('name', '')
    if name == '':
        return redirect(url_for('.index'))
    else:
        return render_template('/chatroom/chat.html')


@socketio.on('join', namespace='/chat')
def join(data):
    print('join', data)
    room = data['room']
    join_room(room)
    session['room'] = room
    name = session.get('name')
    message = '用户:({}) 进入了房间'.format(name)
    d = dict(
        message=message,
    )
    emit('status', d, room=room)


@socketio.on('send', namespace='/chat')
def send(data):
    name = session.get('name')
    message = data.get('message')
    formatted = '{} : {}'.format(name, message)
    print('send', formatted)
    d = dict(
        message=formatted
    )
    room = session.get('room')
    emit('message', d, room=room)


@socketio.on('leave', namespace='/chat')
def leave(data):
    room = session.get('room')
    leave_room(room)
    name = session.get('name')
    d = dict(
        message='{} 离开了房间'.format(name),
    )
    emit('status', d, room=room)