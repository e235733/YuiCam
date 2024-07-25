import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



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

#==================================================
# データベース(モデル)
#==================================================


# ==================================================
# ルーティング
# ==================================================

#最初の画面
@app.route('/')
def base():
    return render_template('base.html')



# 新規登録
@app.route('/signin')
def signin():
    return render_template('signin.html',methods=['GET','POST'])

# ログイン
@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login.html')

# お相手一覧
@app.route('/<int:user_id>',methods=['GET','POST'])
def index():
    return render_template('index.html')

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