from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from .models import User
from . import db
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SeCrEt9KeY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Mydb.db'

REDIS_URL = "redis://localhost:6379/0"
redis_store = FlaskRedis(app)


@app.route('/12345')
def redis_test():
    print(type(redis_store.get('name')))
    return redis_store.get('name')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.app_context():
    db.create_all()

socketio = SocketIO(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', name=current_user.name)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username_or_phone_number = request.form.get('username_or_phone_number')
    password = request.form.get('password')

    user = User.query.filter_by(username=username_or_phone_number).first()

    if not user:
        user = User.query.filter_by(phone_number=username_or_phone_number).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check login credentials.')
        return redirect(url_for('login'))

    login_user(user)
    return redirect(url_for('chat'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')

    user = User.query.filter_by(phone_number=phone_number).first()

    if user:
        flash('There is another user with this phone number.')
        return redirect(url_for('login'))

    new_user = User(username=username, name=name, phone_number=phone_number,
                    password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    name = current_user.name
    logout_user()
    return render_template('logout.html', name=name)


@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
