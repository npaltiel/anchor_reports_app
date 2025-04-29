from flask import Flask, request, render_template, redirect, url_for, session, send_file
from markupsafe import Markup
import datetime
import pytz
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
PASSWORD = 'Hi'
SESSION_TIMEOUT = 1800

@app.before_request
def check_session_timeout():
    """Logout user if inactive for too long."""
    if 'logged_in' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            try:
                # Ensure last_activity is always a string before conversion
                if isinstance(last_activity, str):
                    last_activity = datetime.datetime.fromisoformat(last_activity).replace(tzinfo=pytz.utc)
                elif isinstance(last_activity, (int, float)):  # If it's a timestamp
                    last_activity = datetime.datetime.fromtimestamp(last_activity, tz=datetime.timezone.utc)

                now = datetime.datetime.now(datetime.timezone.utc)  # Use timezone-aware UTC datetime

                if (now - last_activity).total_seconds() > SESSION_TIMEOUT:
                    session.clear()  # Log out user
                    return redirect(url_for('login'))
            except (ValueError, TypeError):
                session.clear()  # Handle invalid session data

        # Store current time as an ISO string
        session['last_activity'] = datetime.datetime.now(datetime.timezone.utc).isoformat()


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
