from flask import Blueprint, render_template, redirect, url_for, request

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Placeholder: validate credentials and redirect
        role = request.form.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'requester':
            return redirect(url_for('requester.dashboard'))
        elif role == 'worker':
            return redirect(url_for('worker.dashboard'))
    return render_template('login.html')
