from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import hashlib
import hmac
import random
import time
import jwt
import sys
import logging

from datetime import datetime
from datetime import timedelta
from datetime import date
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


app = Flask(__name__)
secret_key = 'KYqhqXdnWE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/mac/projects/star_api/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50))
    password = db.Column(db.String)
    last_login = db.Column(db.DateTime)
    last_request = db.Column(db.String)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    likes = db.Column(db.String)
    content = db.Column(db.String(280))

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    liked_by = db.Column(db.String(50))

def token_checking(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers['Authorization']
        print(request.headers, flush=True)
        token = token.replace('Bearer ','')
        token = jwt.decode(token, secret_key, algorithms=['HS256'])
        if token['end_date'] >= int(time.time()):
            return func(token['login'])
        else:
            return jsonify({'token_error': 'Token expired'})
    return wrapper

def last_request(func):
    @wraps(func)
    def wrapper(login, *args, **kwargs):
        print(login, flush=True)
        user = db.session.query(Users).filter_by(login = login).first()
        user.last_request = request.url
        db.session.commit()
        return func(login, *args, **kwargs)
    return wrapper

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    password = hashlib.md5(data['password'].encode('utf-8'))
    password = password.hexdigest()
    new_user = Users(login = data['login'], password = password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'result': 'Registered succesfuly'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = db.session.query(Users).filter_by(login = request.authorization.username).first()
    password = hashlib.md5(request.authorization.password.encode('utf-8'))
    password = password.hexdigest()

    if password == user.password:
        end_date = int(time.time()) + 3600
        token = jwt.encode({'login': request.authorization.username, 'end_date': end_date}, secret_key, 'HS256')
        user.last_login = datetime.now()
        db.session.commit()
        return jsonify({'result': 'Login succesfull', 'token': token.decode('utf-8')})
    else:
        return jsonify({'result': 'Wrong password'})

@app.route('/create_post', methods=['POST'])
@token_checking
@last_request
def create_post(login):
    data = request.get_json()
    try:
        new_post = Posts(author = login, date = datetime.now(), likes = 0, content = data['text'])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'result': 'New post created!'})
    except:
        return jsonify({'result': 'You didn\'t send any text!'})

@app.route('/like', methods=['POST'])
@token_checking
@last_request
def like(login):
    data = request.get_json()
    try:
        like = Likes(post_id = data['id'], date = datetime.now(), liked_by = login)
        post = db.session.query(Posts).filter_by(id = data['id']).first()
        post.likes = int(post.likes) + 1

        db.session.add(like)
        db.session.commit()
        return jsonify({'result': 'Liked succesfuly!'})
    except:
        return jsonify({'result': 'You didn\'t send post id!'})

@app.route('/unlike', methods=['POST'])
@token_checking
@last_request
def unlike(login):
    data = request.get_json()
    try:
        post = db.session.query(Posts).filter_by(id = data['id']).first()
        like = db.session.query(Likes).filter_by(post_id = data['id']).first()
        post.likes = int(post.likes) - 1
        db.session.delete(like)
        db.session.commit()
        return jsonify({'result': 'Unliked succesfuly!'})
    except:
        return jsonify({'result': 'You didn\'t send post id!'})

@app.route('/posts', methods=['GET'])
@token_checking
@last_request
def posts(login):
    posts = db.session.query(Posts).all()
    posts = len(posts)
    return jsonify({'posts': posts})

@app.route('/analytics', methods=['GET'])
@token_checking
@last_request
def analytics(login):
    dict = {}
    try:
        start_date = datetime.strptime(request.args['from'], '%Y-%m-%d').date()
    except:
        return jsonify({'Cannot get \'from\' parameter'})
    try:
        end_date = datetime.strptime(request.args['to'], '%Y-%m-%d').date()
    except:
        return jsonify({'Cannot get \'to\' parameter'})

    while start_date <= end_date:
        posts = db.session.query(Likes).filter(Likes.date >= start_date).filter(Likes.date < start_date + timedelta(days=1)).all()
        dict[str(start_date)] = len(posts)
        start_date += timedelta(days=1)
    return jsonify(dict)

@app.route('/user_activity', methods=['GET'])
@token_checking
@last_request
def user_activity(login):
    try:
        user = db.session.query(Users).filter_by(login = request.args['login']).first()
        return jsonify({'user':user.login,'last_login':user.last_login,'last_request': user.last_request})
    except:
        return jsonify({'error'})

if __name__ == '__main__':
    app.run(debug=True)
