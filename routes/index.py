import os
import uuid
from operator import itemgetter

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory)

from models.reply import Reply
from models.topic import Topic
from models.user import User

from utils import log

main = Blueprint('index', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    if uid != -1:
        u = User.one(id=uid)
    else:
        u = User.one(id=1)
    return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/login/view")
def login_view():
    return render_template("login.html")


@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.login_view'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    print('login user <{}>'.format(u))
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.login_view'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('dou_topic.index'))


@main.route('/profile')
def profile():
    u = current_user()
    ms = Topic.all()
    ms_d = {}
    for c in ms:
        ms_d[str(c.id)] = c.created_time
    ms_d = sorted(ms_d.items(), key=itemgetter(1), reverse=True)
    ms_created = []
    for c in ms_d:
        t = Topic.one(id=int(c[0]), user_id=u.id)
        if t is None:
            continue
        else:
            ms_created.append(t)
    replies = Reply.all(user_id=u.id)
    rs_d = {}
    for r in replies:
        rs_d[str(r.topic_id)] = r.created_time
    rs_d = sorted(rs_d.items(), key=itemgetter(1), reverse=True)
    ms_recented = []
    for r in rs_d:
        print('types', type(r))
        ms_recented.append(Topic.one(id=int(r[0])))
    return render_template(
        "profile.html",
        ms_created=ms_created,
        ms_recented=ms_recented,
        user=u,
    )


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.setting'))


@main.route('/images/<filename>')
def image(filename):
    return send_from_directory('images', filename)


@main.route('/setting')
def setting():
    u = current_user()
    if u is None:
        abort(404)
    else:
        return render_template('setting.html', user=u)


@main.route('/setting/edit', methods=['POST'])
def setting_edit():
    form = request.form.to_dict()
    u = current_user()
    print('check form {}'.format(form))
    User.update(u.id, **form)
    return redirect(url_for('.setting'))


@main.route('/setting/editpwd', methods=['POST'])
def edit_pwd():
    form = request.form.to_dict()
    u = current_user()
    print('check form {}'.format(form))
    if u.password == User.salted_password(form['old_pass']):
        User.update(u.id, password=User.salted_password(form['new_pass']))
        return redirect(url_for('.setting'))
    else:
        print('当前密码不正确')
        return redirect(url_for('.index'))


def not_found(e):
    return render_template('404.html')
