from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)

# Configuration
app.secret_key = "your_secret_key"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'bookstore'

# Initialize MySQL
mysql = MySQL(app)

# Google OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='your_google_client_id',
    client_secret='your_google_client_secret',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            mysql.connection.commit()
            flash("Registration successful. Please log in.", "success")
        except Exception as e:
            flash("An error occurred: " + str(e), "danger")
        finally:
            cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[0]
            flash("Login successful!", "success")
            return redirect(url_for('books'))
        else:
            flash("Invalid credentials, please try again.", "danger")
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    """Login with Google"""
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    """Handle Google OAuth callback"""
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    session['user'] = user_info
    flash(f"Welcome {user_info['name']}! You have logged in with Google.", "success")
    return redirect(url_for('books'))

@app.route('/books')
def books():
    """Books page"""
    if 'user_id' not in session:
        flash("Please log in to access the books.", "warning")
        return redirect(url_for('login'))
    return render_template('books.html')  # Add a books page template

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
