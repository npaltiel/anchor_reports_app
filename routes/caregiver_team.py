from flask import Blueprint, request, render_template, redirect, url_for, session, send_file
import base64
import asyncio
import io
import caregiver_team_scripts.caregiver_team_script as caregiver_team_script
from caregiver_team_scripts.caregiver_team_log import log_run, database
from auth import login_required  # Import login protection


caregiver_team_bp = Blueprint("caregiver_team", __name__)


@caregiver_team_bp.route("/")
@login_required
def caregiver_team_home():
    ref = database.reference("/caregiver_team_logs")
    logs = ref.order_by_key().limit_to_last(50).get() # Get last 50 logs

    logs = list(logs.values())[::-1] if logs else []  # Reverse them for newest first
    return render_template('caregiver_team.html', logs=logs, download_url=url_for("caregiver_team.download_processed"))


@caregiver_team_bp.route('/upload', methods=['POST'])
def upload_files():
    notes = request.files.get('Notes')  # Access file from 'file1' field
    caregivers = request.files.get('Caregivers')  # Access file from 'file2' field
    final = request.files.get('Final')

    # Check if files are uploaded
    if not notes or not caregivers or not final:
        return redirect(url_for('caregiver_team.caregiver_team_home', error="All three files must be uploaded!"))
    
    results, processed_file = asyncio.run(caregiver_team_script.main(notes, caregivers, final))

    log_run(results)

    session['processed_file'] = base64.b64encode(processed_file.getvalue()).decode('utf-8')

    return redirect(url_for('caregiver_team.caregiver_team_home'))


@caregiver_team_bp.route('/download')
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