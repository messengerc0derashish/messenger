from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_socketio import (
    SocketIO,
    emit,
    join_room,
    leave_room
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


online_users = set()

# -------------------- Models --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)

# -------------------- Routes --------------------
@app.route('/')
def index():
    if 'username' in session:
        return redirect(('/chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username.capitalize()).first()
    if user and check_password_hash(user.password, password):
        session['username'] = username.capitalize()
        return redirect(('/chat'))
    return 'Invalid credentials'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return 'User already exists'
        user = User(username=username.capitalize(), password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(('/'))
    return render_template('signup.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(('/'))

    current_user = session['username']
    users = User.query.filter(User.username != current_user).order_by(User.username).all()

    unread_counts = {}
    for user in users:
        count = Message.query.filter_by(sender=user.username, receiver=current_user, is_read=False).count()
        unread_counts[user.username] = count

    return render_template('chat.html', users=users, messages=[], username=current_user, unread_counts=unread_counts)


@app.route('/messages/<receiver_username>', methods=['GET'])
def get_messages(receiver_username):
    current_user = session.get('username')
    if not current_user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    messages = Message.query.filter(
        ((Message.sender == current_user) & (Message.receiver == receiver_username)) |
        ((Message.sender == receiver_username) & (Message.receiver == current_user))
    ).order_by(Message.timestamp).all()

    message_list = [{
        "sender": m.sender,
        "receiver": m.receiver,
        "text": m.text,
        "time": m.timestamp.strftime('%I:%M %p'),
        "is_read": m.is_read
    } for m in messages]

    return jsonify({"status": "success", "messages": message_list})


@app.route('/mark_read', methods=['POST'])
def mark_read():
    data = request.get_json()
    sender = data.get('sender')
    receiver = session.get('username')

    if not sender or not receiver:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    unread_msgs = Message.query.filter_by(sender=sender, receiver=receiver, is_read=False).all()
    for msg in unread_msgs:
        msg.is_read = True

    db.session.commit()
    socketio.emit(
        'messages_read',
        {
            'reader': receiver,
            'sender': sender
        },
        room=sender
    )
    return jsonify({"status": "success", "read_count": len(unread_msgs)})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(('/'))

# -------------------- SocketIO Events --------------------
@socketio.on('join')
def handle_join(data):
    username = data.get('username')

    if not username:
        return

    join_room(username)

    online_users.add(username)

    emit(
        'status',
        {
            'user': username,
            'online': True
        },
        broadcast=True
    )

@socketio.on('disconnect')
def handle_disconnect():

    username = session.get('username')

    if username and username in online_users:

        online_users.remove(username)

        emit(
            'status',
            {
                'user': username,
                'online': False
            },
            broadcast=True
        )

@socketio.on('message')
def handle_message(msg):

    username = session.get('username')

    receiver = msg.get('receiver')
    text = msg.get('text')

    if not username or not receiver or not text:
        return

    india_tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(india_tz)

    message = Message(
        sender=username,
        receiver=receiver,
        text=text,
        timestamp=current_time,
        is_read=False
    )

    db.session.add(message)
    db.session.commit()

    payload = {
        'sender': username,
        'receiver': receiver,
        'text': text,
        'time': current_time.strftime('%I:%M %p'),
        'is_read': False
    }

    emit('message', payload, room=username)
    emit('message', payload, room=receiver)

    emit(
        'new_unread',
        {
            'sender': username
        },
        room=receiver
    )
 
    
# -------------------- Main --------------------
if __name__ == '__main__':
    if not os.path.exists('db.sqlite3'):
        with app.app_context():
            db.create_all()
    socketio.run(app, debug=True)
 