from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField


class GhangeIngoForm(FlaskForm):
    name = StringField('Name of group')
    info = TextAreaField('Info')
    avatar = FileField()
    submit = SubmitField('Submit')