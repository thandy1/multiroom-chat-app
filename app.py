# Bringing in Flask, SocketIO, Flask-Login, password hashing, and database functions
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from dotenv import load_dotenv
from database import get_database_connection, initialize_database

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)   #  Creates Flask application.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Sets the secret key for session encryption.

# Initialize SocketIO for real-time communication
socketio = SocketIO(app)

# Initialize Flask-Login for user session management
login_manager = LoginManager()  # Sets up user authenticaiton system.
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# Initialize database on first run
initialize_database()   # Creates tables if they dont exist yet.

if __name__ == '__main__':
    socketio.run(app, debug=True)