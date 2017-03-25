from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email(), Length(3, 64)])

    username = StringField(
        'Username', validators=[
            DataRequired(), Length(4, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*',
                   message='Username must have Upper/Lower case letters, numbers , dots and underscores')])

    password = PasswordField(
        'Password', validators=[
            DataRequired(), Length(5, 64),
            EqualTo('password2', message='Passwords must match')])

    password2 = PasswordField(
        'Confirm password',
        validators=[DataRequired(), Length(4, 64)])

    submit = SubmitField('submit')

    def validate_email(self, email_field):
        if User.query.filter_by(email=email_field.data).first() is not None:
            raise ValidationError("Email already registered")

    def validate_username(self, username_field):
        if User.query.filter_by(username=username_field.data).first() is not None:
            raise ValidationError("Username already in use")



