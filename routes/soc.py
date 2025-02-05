from flask import Blueprint, request, render_template, redirect, url_for, session, send_file
import os
from datetime import datetime
import io
import soc_scripts.soc_script as soc_script
from soc_scripts.soc_logs import log_run, database


soc_bp = Blueprint("soc", __name__, url_prefix="/soc")
TEMP_FILE_PATH = "temp_soc_file.xlsx"

@soc_bp.route('/')
def soc_home():
    ref = database.reference("/soc_logs")
    logs = ref.order_by_key().limit_to_last(50).get() # Get last 50 logs

    logs = list(logs.values())[::-1] if logs else []  # Reverse them for newest first
    return render_template('soc.html', logs=logs, download_url=url_for("soc.download_processed"))

@soc_bp.route('/upload', methods=['POST'])
def upload_files():
    visits = request.files.get('Visits') 
    patients = request.files.get('Patients')  
    contracts = request.files.get('Contracts')

    # Check if files are uploaded
    if not visits or not patients or not contracts:
        return redirect(url_for('soc.soc_home', upload_error="All three files must be uploaded!"))
    
    results, processed_file = soc_script.main(visits, patients, contracts)

    log_run(results)

    # Save the file temporarily
    with open(TEMP_FILE_PATH, "wb") as f:
        f.write(processed_file.getvalue())

    return redirect(url_for('soc.soc_home'))


@soc_bp.route('/download')
def download_processed():
    # Serve the processed file for download
    processed_file_data = session.pop('processed_file', None)

    if not os.path.exists(TEMP_FILE_PATH):
        return redirect(url_for('soc.soc_home', download_error="No file available for download"))

    date = datetime.today().strftime('%B %Y')

    # Serve the file and delete it after download
    response = send_file(
        TEMP_FILE_PATH,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'SOC_{date}.xlsx'
    )

    return response