from flask import session, redirect, url_for
from functools import wraps

def login_required(func):
    """Decorator to protect Blueprint routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper
