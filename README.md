# Messenger Chat App

A real-time web-based messenger application built with Flask, Socket.IO, SQLAlchemy, and SQLite.

## Features

- User Registration & Login
- Secure Password Hashing
- Real-Time Messaging
- Message Persistence
- Unread Message Counter
- Dark Mode Support
- Responsive Mobile-Friendly UI
- Session-Based Authentication

## Tech Stack

### Backend

- Flask
- Flask-SocketIO
- Flask-SQLAlchemy
- SQLite
- Eventlet

### Frontend

- HTML5
- CSS3
- JavaScript
- Socket.IO Client

## Screenshots

### Login Page

![Login](screenshots/login.png)

### Signup Page

![Signup](screenshots/signup.png)

### Chat Interface

![Chat](screenshots/chat.png)

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/messenger-chat-app.git
cd messenger-chat-app
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open

```text
http://127.0.0.1:5000
```

## Project Structure

```text
Messenger-App/
│
├── app.py
├── requirements.txt
├── templates/
├── static/
└── screenshots/
```

## Database

SQLite is used for development.

Tables:

### User

| Field    | Type    |
|-----------|----------|
| id        | Integer |
| username  | String |
| password  | String |

### Message

| Field      | Type |
|------------|------|
| sender     | String |
| receiver   | String |
| text       | String |
| timestamp  | DateTime |
| is_read    | Boolean |

## Future Improvements

- Online/Offline Status
- Typing Indicators
- Profile Pictures
- Group Chats
- Message Reactions
- File Sharing
- Voice Messages
- MySQL/PostgreSQL Migration

## Author

Ashish Chandra

B.Tech CSE | Software Developer

## License

MIT License