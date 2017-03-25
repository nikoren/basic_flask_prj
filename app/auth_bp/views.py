from flask import render_template, redirect, request, url_for, flash
from flask_login import logout_user, login_required, login_user
from . import auth_bp
from ..models import User
from .forms import LoginForm,RegistrationForm
from .. import db


@auth_bp.route('/register', methods=['GET','POST'])
def register():
    registration_form = RegistrationForm()

    # if POST
    if registration_form.validate_on_submit():
        user = User(username=registration_form.username.data,
                    email=registration_form.email.data,
                    password=registration_form.password.data)
        db.session.add(user)
        # db.session.commit() # We might be don't need to commit the session as flask does it for use for each request

        # we should have only one place to login users, don't login from register
        return redirect(url_for('auth_bp.login'))

    # if GET
    return render_template('auth_bp/register.html', registration_form=registration_form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    # if POST
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.password_is_correct(login_form.password.data):

            # login_user takes the user to log in and an optional remember me Boolean,
            # which was also submitted with the form.
            # A value of False for this argument causes the user session to expire when the browser window is closed,
            # so the user will have to log in again next time.  A value of True causes a long-term cookie
            # to be set in the users browser and with that the user session can be restored.
            login_user(user, login_form.remember_me.data)

            # post request should end with redirect for browser reloading compatibility
            # If the login form was presented to the user to prevent unauthorized access to a protected URL,
            # then Flask-Login saved the original URL in the next query string argument,
            # which can be accessed from the request.args dictionary.
            return redirect(request.args.get('next') or url_for('main_bp.index'))

        flash('Invalid username or password.', category='danger')

    # if GET
    return render_template('auth_bp/login.html', login_form=login_form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='warning')
    return redirect(url_for('main_bp.index'))
