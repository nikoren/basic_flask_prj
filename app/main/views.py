from . import main_blueprint
from . import forms
from .. import models
from .. import db
from flask import session, redirect, flash, url_for, render_template
from flask_login import login_required

@main_blueprint.route('/', methods=['POST','GET'])
def index():
    form = forms.NameForm()

    # IF POST - form need to be processed, otherwise just render the form
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Create new user
            user = models.User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))

    return render_template(
        'index.html', form=form, name=session.get('name'),
        known=session.get('known', False))


@main_blueprint.route('/clear_session/<value>')
@login_required
def clear_session(value='all'):
    if value != 'all':
        if value in session.keys():
            session[value] = None
            flash('{} was removed from session'.format(value))
    else:
        session.clear()
        flash('Session was cleared', category='danger')
    return redirect(url_for('.index'))