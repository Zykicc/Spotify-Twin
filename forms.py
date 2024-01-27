from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, DataRequired



class LoginForm(FlaskForm):
  """Login form."""

  username = StringField('Enter your username', validators=[DataRequired()])
  password = PasswordField('Enter your password', validators=[Length(min=6)])

class SignUpForm(FlaskForm):
    """Form for adding users."""

    username = StringField(' Create Username', validators=[DataRequired()])
    email = StringField('Enter your E-mail', validators=[DataRequired()])
    password = PasswordField('Create Password', validators=[Length(min=6)])


class GetUser1(FlaskForm):
   """Form for getting user 1 playlists"""

   user1_id = StringField('', validators=[DataRequired()])


class GetUser2(FlaskForm):
   """Form for getting user 2 playlists"""

   user2_id = StringField('', validators=[DataRequired()])