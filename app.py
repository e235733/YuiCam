import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from forms import SigninForm,LoginForm,ProfileForm

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# Flaskに対する設定
# ==================================================
# 乱数を設定
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ★db変数を使用してSQLAlchemyを操作できる
db = SQLAlchemy(app)
# ★「flask_migrate」を使用できる様にする
Migrate(app, db)

#==================================================
# データベース(モデル)
#==================================================
#@login_manager.user_loader
#def load_user(user_id):
#    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    # Userテーブル
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.Integer, nullable=False)
    univ_year = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.String(160))
    profile_picture = db.Column(db.LargeBinary)

    # リレーションシップ
    likes_given = db.relationship('Like', foreign_keys='Like.liker_id', backref='liker', lazy='dynamic')
    likes_received = db.relationship('Like', foreign_keys='Like.liked_id', backref='liked', lazy='dynamic')
    matches = db.relationship('Match', 
                              primaryjoin="or_(Match.user1_id==User.id, Match.user2_id==User.id)",
                              backref='users', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def like(self, user):
        if not self.has_liked(user):
            like = Like(liker_id=self.id, liked_id=user.id)
            db.session.add(like)
            db.session.commit()

    def unlike(self, user):
        Like.query.filter_by(liker_id=self.id, liked_id=user.id).delete()
        db.session.commit()

    def has_liked(self, user):
        return Like.query.filter(
            Like.liker_id == self.id,
            Like.liked_id == user.id).count() > 0

class Like(db.Model):
    __tablename__ = 'like'
    
    # Likeテーブル
    id = db.Column(db.Integer, primary_key=True)
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    liked_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Match(db.Model):
    __tablename__ = 'match'
    
    # Matchテーブル
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @classmethod
    def create_match(cls, user1, user2):
        match = cls(user1_id=user1.id, user2_id=user2.id)
        db.session.add(match)
        db.session.commit()
        return match

# ==================================================
# ルーティング
# ==================================================

#最初の画面
@app.route('/')
def base():
    return render_template('base.html')



# 新規登録
@app.route('/signin',methods=['GET','POST'])
def signin():
    #フォームの作成
    form = SigninForm(request.form)
    #POST
    if request.method == "POST" and form.validate():
        username = request.form['username']    #['username']はHTMLフォームの入力フィールドのname属性から来ている
        email = request.form['email']
        password = request.form['password']  

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # エラーメッセージをフラッシュしてリダイレクト
            # flash('Email address already exists')
            return redirect(url_for('signin'))

        #新しいユーザーの作成
        new_user = User(username=username,email=email,faculty=0,univ_year=1)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index',user_id=new_user.id))
        
    return render_template('signin.html',form=form)

# ログイン
@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login.html')

# お相手一覧
@app.route('/<int:user_id>',methods=['GET','POST'])
def index(user_id):
    users = User.query.all()
    return render_template('index.html',users=users)

# プロフィール詳細
@app.route('/<int:user_id>/profile_detail',methods=['GET','POST'])
def profile_detail():
    return render_template('profile_detail.html')

# マッチングリスト
@app.route('/<int:user_id>/matching_list')
def matching_list():
    return render_template('matching_list.html')

# いいねリスト
@app.route('/<int:user_id>/like_list',methods=['GET','POST'])
def like_list():
    return render_template('like_list.html')

# プロフィール編集
@app.route('/<int:user_id>/profile_edit',methods=['GET','POST'])
def profile_edit():
    return render_template('profile_edit.html')

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(debug=True)