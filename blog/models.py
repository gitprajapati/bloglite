from . import db
from flask_login import UserMixin
import datetime


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200))
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    profile_pic = db.Column(db.String(), nullable=True)
    created = db.Column(db.DateTime(), default=datetime.date.today())
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def like(self, post):
        if not self.liked(post):
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike(self, post):
        if self.liked(post):
            Like.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def liked(self, post):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.post_id == post.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            followed_user = Follow(follower=self, followed=user)
            db.session.add(followed_user)

    def unfollow(self, user):
        unfollowed_user = self.followed.filter_by(followed_id=user.id).first()
        if unfollowed_user:
            db.session.delete(unfollowed_user)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    image = db.Column(db.String)
    post_created = db.Column(db.DateTime, default=datetime.date.today())
    poster_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)


class Like(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comment = db.Column(db.String, nullable=False)
    comment_created = db.Column(db.DateTime(), default=datetime.date.today())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)
