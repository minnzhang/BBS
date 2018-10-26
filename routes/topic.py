from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board
from models.user import User
from routes import (
    current_user,
    new_csrf_token,
    csrf_required,
)

from models.topic import Topic



main = Blueprint('dou_topic', __name__)


@main.route("/")
def index():
    u = current_user()
    print('minn---u', User.all(), u)
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    # token = new_csrf_token()
    bs = Board.all()
    return render_template("topic/index.html", ms=ms, user=u, bs=bs, bid=board_id)


@main.route('/<int:id>')

def detail(id):
    m = Topic.get(id)
    return render_template("topic/detail.html", topic=m)


@main.route("/new")
def new():
    board_id = int(request.args.get('board_id'))
    bs = Board.all()
    token = new_csrf_token()
    print('bug---token')
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)



@main.route("/add", methods=["POST"])
@csrf_required
def add():
    u = current_user()
    form = request.form.to_dict()
    t = Topic.add(form, user_id=u.id)
    return redirect(url_for('.detail', id=t.id))