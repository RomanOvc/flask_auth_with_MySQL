from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from app import db
from app.auth import auth
from app.email import send_email
from app.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = db.session.query(User).filter(User.email == email).first()
        passw = db.session.query(User).filter(User.password == password).first()
        if not user or not passw or user.email != email or user.password != password:
            flash('Пожалуйста, проверьте данные для входа и попробуйте снова.')
            return redirect(url_for('auth.login'))
        else:
            login_user(user)
            return redirect(url_for('main.profile'))
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        ema = request.form['email']
        password = request.form['password']
        if username == '' or ema == '' or password == '':
            flash('Пожалуйста, проверьте данные')
        else:
            user = User(username=username, email=ema, password=password)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            print(token)
            send_email(user.email, 'Confirm Your Account',
                       'auth/email/confirm', user=user, token=token)
            flash('Письмо с подтверждением было отправлено вам по электронной почте.')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Вы подтвердили свой аккаунт. Спасибо!')
    else:
        flash('Ссылка для подтверждения недействительна или устарела.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
