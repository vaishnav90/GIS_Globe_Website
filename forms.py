from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, URL, Optional
from cloud_storage import cloud_storage

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = cloud_storage.get_user_by_username(username.data)
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = cloud_storage.get_user_by_email(email.data)
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=200)])
    creator_name = StringField('Creator Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    project_link = StringField('Project Link', validators=[DataRequired(), URL()])
    project_type = SelectField('Project Type', choices=[
        ('Hub Page', 'Hub Page'),
        ('Form', 'Form'),
        ('Feature Service', 'Feature Service'),
        ('Dataset', 'Dataset'),
        ('Survey123', 'Survey123'),
        ('Web App', 'Web App'),
        ('Dashboard', 'Dashboard'),
        ('Story Map', 'Story Map'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)', validators=[Length(max=500)])
    image_url = StringField('Image URL (optional - will auto-detect if left empty)', validators=[Length(max=500)])
    image_file = FileField('Or upload image from computer', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Add Project')

class GalleryForm(FlaskForm):
    title = StringField('Image Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_file = FileField('Upload Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Add to Gallery') 