from flask import Flask, request, render_template, redirect, url_for, session, send_file
from markupsafe import Markup
import base64
import asyncio
import io
import caregiver_team_update  # Import your script here
from log import log_run, db

app = Flask(__name__)
app.secret_key = 'ANCH1234'

@app.route('/')
def home():
    ref = db.reference("/logs")
    logs = ref.order_by_key().limit_to_last(50).get() # Get last 50 logs

    logs = list(logs.values())[::-1] if logs else []  # Reverse them for newest first

    return render_template('index.html', logs=logs)

@app.route('/upload', methods=['POST'])
def upload_files():
    notes = request.files.get('Notes')  # Access file from 'file1' field
    caregivers = request.files.get('Caregivers')  # Access file from 'file2' field
    final = request.files.get('Final')

    # Check if files are uploaded
    if not notes or not caregivers or not final:
        return redirect(url_for('home', error="All three files must be uploaded!"))
    
    results, processed_file = asyncio.run(caregiver_team_update.main(notes, caregivers, final))

    log_run(results)

    session['processed_file'] = base64.b64encode(processed_file.getvalue()).decode('utf-8')


    return redirect(url_for('home'))  # Return the results

@app.route('/caregiver_team')
def caregiver_team_update():
    return render_template('caregiver_team.html')

@app.route('/soc')
def soc_report():
    return render_template('soc.html')

@app.route('/download')
def download_processed():
    # Serve the processed file for download
    processed_file_data = session.pop('processed_file', None)

    # Decode the Base64 string back into a BytesIO object
    processed_file = io.BytesIO(base64.b64decode(processed_file_data))

    return send_file(
        processed_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name='Disciplinary Final (Updated).csv'
    )
    
    
if __name__ == '__main__':
    app.run(debug=True)
