from flask import render_template, redirect, request, url_for, flash
from flask_login import logout_user, login_required, login_user, current_user
from . import auth_bp
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from ..email import send_email


@auth_bp.before_app_request
def before_request():
    '''
    Only show page that asks them to confirm accounts before they can gain access.
    This is happenining before each request, so attempts to access any other then
    auth content is intercepted and redirected to confirmation url
    '''

    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint  \
            and request.endpoint[:5] != 'auth_bp.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth_bp.unconfirmed'))


@auth_bp.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main_bp.index'))
    return render_template('auth_bp/unconfirmed.html')


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


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()

    # if POST
    if registration_form.validate_on_submit():
        user = User(username=registration_form.username.data,
                    email=registration_form.email.data,
                    password=registration_form.password.data)
        db.session.add(user)
        db.session.commit()  # Commit to have an id populated

        token = user.generate_confirmation_token()

        send_email(user.email, 'Confirm your account', 'auth_bp/email/confirm', token=token, user=user)
        flash('A confirmation email has been sent to your email')
        # we should have only one place to login users, don't login from register
        return redirect(url_for('auth_bp.login'))

    # if GET
    return render_template('auth_bp/register.html', registration_form=registration_form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    '''
    This is personal confirmation route function for each user based on his own id
    Link to route of this function sent to user and he clicks it from his email
    route is protected with the login_required decorator from Flask-Login,
    so that when the users click on the link from the confirmation email
    they are asked to log in before they reach this view function.
    '''
    current_user.logger.debug('Starting to confirm {} account'.format(current_user))
    if current_user.confirmed:
        # User has already finish email confirmation
        return redirect(url_for('main_bp.index'))

    if current_user.confirm_valid_token(token):
        flash('You have completed your account!', category='success')
    else:
        flash('The confirmation link is invalid or expired.')

    return redirect(url_for('main_bp.index'))


@auth_bp.route('/confirm')
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'auth_bp/email/confirm',
               'Confirm Your Account', token=token, user=current_user)
    flash('A new confirmation email has been sent to you')
    return redirect(url_for('main.index'))
