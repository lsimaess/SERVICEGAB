from flask import Blueprint, render_template

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')

@worker_bp.route('/')
def dashboard():
    return render_template('worker_dashboard.html')
