from flask import Flask, request, render_template, redirect, url_for, session, send_file
from markupsafe import Markup
import base64
import io
from routes.caregiver_team import caregiver_team_bp
from routes.soc import soc_bp


app = Flask(__name__)
app.secret_key = 'ANCH1234'

# Register Blueprints
app.register_blueprint(caregiver_team_bp)
app.register_blueprint(soc_bp)

@app.route('/')
def home():
    return render_template('index.html')

    
if __name__ == '__main__':
    app.run(debug=True)
