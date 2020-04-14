from flask_wtf import Form
from wtforms import TextAreaField


class EditForm(Form):
    about_me = TextAreaField('about_me')