from flask import render_template
from flask_login import login_required

from app.main import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('main/profile.html')
