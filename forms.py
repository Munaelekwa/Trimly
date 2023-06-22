from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError,Length

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_field(self, email):

        user = user.query.filter_by(email=email.data).first()
        if True:
            raise ValidationError('Email Already registered!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

class NewLinkForm(FlaskForm):
    title = StringField('title', validators=[Length(max=15, message='Maximum length is 15 characters.')])
    long_url = TextAreaField('long url', validators=[DataRequired()])
    custom_url = StringField('custom url', validators=[Length(max=15, message='Maximum length is 15 characters.')])
    submit = SubmitField('Shorten')

class NewQrcodeForm(FlaskForm):
    title = StringField('title', validators=[Length(max=15, message='Maximum length is 15 characters.')])
    url = TextAreaField('url', validators=[DataRequired()])
    submit = SubmitField('Generate')

