from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired



class GetUser1(FlaskForm):
   """Form for getting user 1 playlists"""

   user1_id = StringField('', validators=[DataRequired()])


class GetUser2(FlaskForm):
   """Form for getting user 2 playlists"""

   user2_id = StringField('', validators=[DataRequired()])