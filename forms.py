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
class SigninForm(Form):
    username = StringField(validators=[DataRequired('名前は必須入力です')])
    email = StringField(validators=[Email('メールアドレスを書いてください')])
    password = PasswordField()



#ログインクラス
class LoginForm(Form):
    username = StringField(validators=[DataRequired('名前は必須入力です')])
    email = StringField()
    password = PasswordField()


#プロフィール情報クラス
class ProfileForm(Form):
    username = StringField(validators=[DataRequired('名前は必須入力です')])
    faculty = IntegerField()
    univ_year = IntegerField()
    bio = TextAreaField()
    profile_picture = FileField()
    submit = SubmitField()

