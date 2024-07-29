from wtforms import Form
from wtforms.fields import (
    StringField, IntegerField, PasswordField, DateField, 
    RadioField, SelectField, BooleanField, TextAreaField,
    FileField, SubmitField
    )
from wtforms.validators import (
    Length,DataRequired,Email,EqualTo,NumberRange,InputRequired
    )

from flask_wtf import FlaskForm

#新規登録クラス
class SigninForm(Form):
    username = StringField(validators=[DataRequired('名前は必須入力です')])
    email = StringField(validators=[Email('メールアドレスを書いてください')])
    password = PasswordField()



#ログインクラス
class LoginForm(Form):
    email = StringField()
    password = PasswordField()


#プロフィール情報クラス
class ProfileForm(FlaskForm):
    username = StringField('名前', validators=[DataRequired()])
    faculty = SelectField(
        '学部',
        choices=[(0, '人文社会学部'), (1, '国際地域創造学部'), (2, '教育学部'), (3, '理学部'), (4, '医学部'), (5, '工学部'), (6, '農学部')],
        coerce=int,
        validators=[InputRequired()]
    )
    univ_year = IntegerField('学年', validators=[DataRequired()])
    bio = TextAreaField('自己紹介')
    profile_picture = FileField('プロフィール写真')
    submit = SubmitField('保存')
