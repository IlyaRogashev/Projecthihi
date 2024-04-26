from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class PForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    file = FileField("Содержание")
    submit = SubmitField('Применить')