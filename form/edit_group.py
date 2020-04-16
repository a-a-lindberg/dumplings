from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError


def len_info(field):
    if len(field.data) > 85:
        raise ValidationError('Info must be less than 85 characters')


class GhangeIngoForm(FlaskForm):
    name = StringField('Name of group')
    info = StringField('Info', len_info)
    submit = SubmitField('Submit')