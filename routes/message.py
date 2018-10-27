from flask_mail import Message, Mail
from flask import (
    render_template,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Messages

main = Blueprint('mail', __name__)
mail = Mail()


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    form['receiver_id'] = int(form['receiver_id'])
    u = current_user()
    form['sender_id'] = u.id
    m = Messages.new(form)
    return redirect(url_for('.index'))


@main.route('/')
def index():
    u = current_user()

    sent_mail = Messages.all(sender_id=u.id)
    received_mail = Messages.all(receiver_id=u.id)

    t = render_template(
        'mail/index.html',
        send=sent_mail,
        received=received_mail,
    )
    return t


@main.route('/view/<int:id>')
def view(id):
    mail = Messages.one(id=id)
    u = current_user()
    if u.id in [mail.receiver_id, mail.sender_id]:
        return render_template('mail/detail.html', mail=mail)
    else:
        return redirect(url_for('.index'))
