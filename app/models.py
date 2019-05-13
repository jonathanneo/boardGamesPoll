from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin       # used for logins
from hashlib import md5
from time import time
import jwt

# followers association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# votes association table
votes = db.Table('votes',
    db.Column('id_option', db.Integer, db.ForeignKey('option.id')),
    db.Column('id_user', db.Integer, db.ForeignKey('user.id'))
)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    id_poll = db.Column(db.Integer, db.ForeignKey('poll.id'))
    
    def voters(self):
        return db.session.query(votes).filter(votes.id_option == self.id).count()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    polls = db.relationship('Poll', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    votes = db.relationship(
        'Option', secondary = votes, 
        primaryjoin=(votes.c.id_user == id),
        backref=db.backref('voters', lazy='dynamic'), lazy='dynamic')

    def vote(self, option):
        if not self.has_voted_option(option):
            self.votes.append(option)
    
    def unvote(self,option):
        if self.has_voted_option(option):
            self.votes.remove(option)

    def has_voted_option(self, option):
        return db.session.query(votes).filter(votes.c.id_option == option.id, votes.c.id_user == self.id).count() > 0

    def has_voted_poll(self, poll):
        return Option.query.join(votes, Option.id == votes.c.id_option).filter(Option.id_poll == poll.id).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def followed_polls(self):   # complicated query - read blog post if do not understand
        followed = Poll.query.join(
            followers, (followers.c.followed_id == Poll.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Poll.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Poll.timestamp.desc()) 
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(140))
    image_url = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<Poll {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
