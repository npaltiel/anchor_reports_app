from flask import Flask, request, render_template, redirect, url_for, session, send_file
from markupsafe import Markup
import base64
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
