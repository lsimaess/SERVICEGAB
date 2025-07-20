from flask import Blueprint, render_template

requester_bp = Blueprint('requester', __name__, url_prefix='/requester')

@requester_bp.route('/')
def dashboard():
    return render_template('requester_dashboard.html')
