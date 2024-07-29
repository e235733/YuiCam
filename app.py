import os
from flask import Flask, render_template, request, redirect, url_for,flash, session, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField, SubmitField
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename

from forms import SigninForm,LoginForm,ProfileForm

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# 画像の処理
# ==================================================
# アップロード先のディレクトリを指定
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path,'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

         # マッチが存在するかチェック
        match = Match.query.filter(
            db.or_(
                db.and_(Match.user1_id == self.id, Match.user2_id == user.id),
                db.and_(Match.user1_id == user.id, Match.user2_id == self.id)
            )
        ).first()

        if match:
            db.session.delete(match)
            
        db.session.commit()

    def has_liked(self, user):
        return Like.query.filter(
            Like.liker_id == self.id,
            Like.liked_id == user.id).count() > 0
    
    def toggle_like(self, user):
        if self.has_liked(user):
            self.unlike(user)
            return False
        else:
            self.like(user)
            return True

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

#ユーザーがログインしているか確認するセッション管理
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_faculty_name(faculty_id):
    faculty_dict = {
        0: '人文社会学部',
        1: '国際地域創造学部',
        2: '教育学部',
        3: '理学部',
        4:'医学部',
        5:'工学部',
        6:'農学部'
    }
    return faculty_dict.get(faculty_id, '不明な学部')

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
            flash('Email address already exists')
            return redirect(url_for('signin'))

        #新しいユーザーの作成
        new_user = User(username=username,email=email,faculty=0,univ_year=1,profile_picture='static/uploads/placeholder.jpg')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index',user_id=new_user.id))
        
    return render_template('signin.html',form=form)

# ログイン
@app.route('/login',methods=['GET','POST'])
def login():
    #フォームの作成
    form = LoginForm(request.form)
    #POST
    if request.method == "POST" and form.validate():
        email = request.form['email']
        password = request.form['password']  

        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            #エラーメッセージをフラッシュしてリダイレクト
            flash('Invalid email or password')
            return redirect(url_for('login'))
        
        session['user_id'] = user.id

        return redirect(url_for('index',user_id=user.id))
        
    return render_template('login.html',form=form)

#ログアウト
@app.route('/logout')
@login_required
def logout():
    # セッションからユーザーIDを削除してログアウト
    session.pop('user_id', None)
    return redirect(url_for('login'))

# お相手一覧
@app.route('/<int:user_id>',methods=['GET','POST'])
@login_required
def index(user_id):
    if user_id != session.get('user_id'):
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('index.html',users=users)

# プロフィール詳細
@app.route('/<int:user_id>/profile_detail', methods=['GET', 'POST'])
@login_required
def profile_detail(user_id):
    if user_id != session.get('user_id'):
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    faculty_name = get_faculty_name(user.faculty)

    return render_template('profile_detail.html', user=user, faculty_name=faculty_name)

# マッチングリスト
@app.route('/<int:user_id>/matching_list')
@login_required
def matching_list(user_id):
    if user_id != session.get('user_id'):
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    # マッチしたユーザーを取得
    matched_users = []
    for match in user.matches:
        if match.user1_id == user.id:
            matched_users.append(User.query.get(match.user2_id))
        else:
            matched_users.append(User.query.get(match.user1_id))

    return render_template('matching_list.html',matched_users=matched_users)

# いいねリスト
@app.route('/<int:user_id>/like_list',methods=['GET','POST'])
@login_required
def like_list(user_id):
    if user_id != session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('like_list.html')

# プロフィール編集
@app.route('/<int:user_id>/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit(user_id):
    if user_id != session.get('user_id'):
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    form = ProfileForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.faculty = form.faculty.data
        user.univ_year = form.univ_year.data
        user.bio = form.bio.data
        
        if form.profile_picture.data:
            file = form.profile_picture.data
            if allowed_file(file.filename):
                user.profile_picture = file.read()
                                     
        db.session.commit()
        return redirect(url_for('profile_detail', user_id=user.id))
    
    if request.method == 'POST' and not form.validate_on_submit():
        print(f"フォームのデータ: {form.data}")
        print(f"バリデーションエラー: {form.errors}")
    
    return render_template('profile_edit.html', form=form, user=user)

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_picture:
        return Response(user.profile_picture, mimetype='image/jpeg')  # MIMEタイプは適切に設定
    return send_file('static/uploads/placeholder.jpg')

@app.route('/like/<int:liked_id>', methods=['POST'])
@login_required
def like(liked_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    liked_user = User.query.get(liked_id)

    if not user or not liked_user:
        # flash('User not found.')
        return redirect(url_for('index', user_id=user_id))

    if user.toggle_like(liked_user):
        if liked_user.has_liked(user):
            Match.create_match(user, liked_user)
            # flash('It\'s a match!')
    #     else:
    #         flash('Liked.')
    # else:
    #     flash('Like removed.')

    return redirect(url_for('index', user_id=user_id))
# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(debug=True)