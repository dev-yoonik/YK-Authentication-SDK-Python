from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional


class FaceAuthenticationForm(FlaskForm):
    """Face Authentication Form."""
    user_id = StringField('user_id', validators=[Optional()])
    user_selfie = StringField('user_selfie', validators=[DataRequired()])
