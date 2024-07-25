import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# Flaskに対する設定
# ==================================================


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
    username = db.Column(db.String(30), unique=True, nullable=False)
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
# 一覧
@app.route('/')
def base():
    return render_template('base.html')

@app.route('/index')
def index():
    return render_template('index.html')

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(debug=True)