from wtforms import Form
from wtforms.fields import (
    StringField, IntegerField, PasswordField, DateField, 
    RadioField, SelectField, BooleanField, TextAreaField,
    FileField, SubmitField
    )
from wtforms.validators import (
    Length,DataRequired,Email,EqualTo,NumberRange
    )

#新規登録クラス
class Signin(Form):
    username = StringField('username:',validators=[DataRequired('名前は必須入力です')])
    email = StringField('email:',validators=[Email('メールアドレスを書いてください')])
    password = PasswordField('password:')



#ログインクラス
class Login(Form):
    username = StringField('username:',validators=[DataRequired('名前は必須入力です')])
    email = StringField('email:')
    password = PasswordField('password:')


#プロフィール情報クラス
class Signin(Form):
    username = StringField('username:',validators=[DataRequired('名前は必須入力です')])
    faculty = IntegerField('学部:')
    univ_year = IntegerField('学年:')
    bio = TextAreaField('自己紹介:')
    profile_picture = FileField('画像更新')
    submit = SubmitField('更新')

