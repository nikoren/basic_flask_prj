from flask import Flask, session, redirect, url_for , render_template, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
Bootstrap(app)
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db=db)
manager.add_command('DB', MigrateCommand)


class NameForm(Form):
    name = StringField('what is your name?',validators=[Required()])
    submit = SubmitField('submit')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' % self.username



app.config['SECRET_KEY'] = 'hard to guess string'

@app.route('/clear_session/<value>')
def clear_session(value='all'):
    if value != 'all':
        if value in session.keys():
            session[value] = None
    else:
        session.clear()
    return redirect(url_for('index'))


@app.route('/', methods=['POST','GET'])
def index():
    form = NameForm()

    # IF POST - form need to be processed, otherwise just render the form
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Create new user
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))

    return render_template(
        'index.html', form=form, name=session.get('name'),
        known=session.get('known', False))


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))




if __name__ == '__main__':
    # app.run(debug=True, port=5002)
    manager.run()
