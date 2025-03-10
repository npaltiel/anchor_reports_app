from flask import Flask, request, render_template, redirect, url_for, session, send_file
from markupsafe import Markup
import datetime
import os
from routes.caregiver_team import caregiver_team_bp
from routes.soc import soc_bp
from auth import login_required  # Import login protection


app = Flask(__name__)
app.secret_key = 'ANCH1234'

# Register Blueprints
app.register_blueprint(caregiver_team_bp, url_prefix="/caregiver_team")
app.register_blueprint(soc_bp, url_prefix="/soc")

PASSWORD = os.getenv("APP_PASSWORD")

@app.before_request
def check_session_timeout():
    """Logout user if inactive for too long."""
    if 'logged_in' in session:
        last_activity = session.get('last_activity')
        if last_activity and (datetime.datetime.now() - last_activity).total_seconds() > 1800:
            session.clear()  # Log out user
            return redirect(url_for('login'))
        session['last_activity'] = datetime.datetime.now()  # Update last activity timestamp


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page"""
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "Invalid Password. Try again.", 401

    return '''
        <form method="post">
            Password: <input type="password" name="password"><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    """Logout Page"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """Homepage (Protected)"""
    return render_template('index.html')

    
if __name__ == '__main__':
    app.run(debug=True)
