from flask import Blueprint, request, render_template, redirect, url_for, session, send_file
import base64
import asyncio
import io
import caregiver_team_script  # Import your script here
from log import log_run, db

soc_bp = Blueprint("soc", __name__, url_prefix="/soc")


@soc_bp.route('/soc')
def soc_report():
    return render_template('soc.html')