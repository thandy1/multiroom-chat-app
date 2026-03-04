import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from dotenv import load_dotenv
from database import get_database_connection, initialize_database

# Load environment variables from .env file.
load_dotenv()

# Creates Flask application.
app = Flask(__name__)   

# Sets the secret key for session encryption so users cant tamper with session data.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  

# Initialize SocketIO for real-time communication.
socketio = SocketIO(app)

# Creates a login manager that handles user sessions.
login_manager = LoginManager()  
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated.

# Initialize database on first run.
initialize_database()  

class User:
    """Represent a logged-in user to check user status."""
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # May need to override this if needed.
    def get_id(self):
        """Returns the user ID that gets stored in the session cookie."""
        return str(self.user_id)

@login_manager.user_loader  # Sets the callback for reloading a user from the session.
def load_user(user_id):
    """
    Loads a User object from the database using the user_id stored in the session cookie.
    This runs automatically on every request where a user is logged in.
    """
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            '''SELECT user_id, username, email FROM users where user_id = ?''', (user_id,)
        )

        # Fetch the data and check if it exists.
        user_row = db_cursor.fetchone()
        if user_row is not None:
            return User(
                user_row['user_id'], 
                user_row['username'], 
                user_row['email']
                )
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    GET: Display registration form.
    POST: Process form submission, hash password, insert new user into database.
    """
    if request.method == 'POST':
        # If the request method is POST, retrieve form data.
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ''
        # Hash the password for security.
        hashed_password = generate_password_hash(password) 
        # Try to insert the form data into the database.
        try:
            with get_database_connection() as database_connection:
                db_cursor = database_connection.cursor()
                db_cursor.execute(
                    '''INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)''', (username, email, hashed_password)
                )
        # Handle potential errors.
        except sqlite3.IntegrityError:
            flash("Username already exists,", 'error')
        # On success (no errors).
        else:
            flash("Registration successful! Please log in.", 'success')
            return redirect(url_for('login'))

    # If the request method is GET, render the template
    # (or if POST failed and flashed error).
    return render_template('register.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)