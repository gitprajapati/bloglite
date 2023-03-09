from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Like, Comment, Post
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from flask import current_app as app
import uuid
from sqlalchemy import update
auth = Blueprint('auth', __name__)


@auth.route('/loogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first(
        )
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                return redirect('/')
            else:
                flash('Incorrect password, please try again.', category='warning')
        else:
            flash('Email does not exist.', category='warning')
    logout_user()
    return render_template("login.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/loogin')


@auth.route('/register', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['f_name']
        last_name = request.form['l_name']

        password1 = request.form['password1']
        password2 = request.form['password2']
        username = request.form['username']
        profile_pic = request.files['profile_pic']

        if profile_pic:

            profile_pic_name = secure_filename(profile_pic.filename)
            pic_name = str(uuid.uuid1())+"__" + profile_pic_name
            profile_pic.save(os.path.join(
                app.root_path, 'static\\profile_pics', pic_name))

        else:
            pic_name = ""

        user = User.query.filter_by(email=email).first()
        usrname = User.query.filter_by(username=username).first()
        if user:
            flash('Email already exists.', category='warning')
        elif usrname:
            flash('Username already exists.', category='warning')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='warning')
        elif password1 != password2:
            flash('Passwords are not matching.', category='warning')
        elif len(password1) < 6:
            flash('Password must have at least 6 characters.', category='warning')

        else:
            new_user = User(email=email, first_name=first_name.title(), password=generate_password_hash(
                password1, method='sha256'), last_name=last_name.title(), profile_pic=pic_name, username=username)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('You are logged in, Account created successfully.',
                  category='success')
            return redirect('/')

    return render_template("register.html")


@auth.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('No user found with username {}.'.format(
            username), category='warning')
        return redirect(url_for('views.home'))
    if user == current_user:
        flash('You cannot follow yourself.', category='warning')
        return redirect(url_for('views.home'))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}.'.format(username))
    return redirect(url_for('views.other_profile', username=username))


@auth.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('No user found with username {}.'.format(
            username), category='warning')
        return redirect(url_for('views.home'))
    if user == current_user:
        flash('You cannot unfollow yourself.')
        return redirect(url_for('views.home'), category='warning')
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}.'.format(username), category='success')
    return redirect(url_for('views.other_profile', username=username))


@auth.route('/profile/<user_id>/update', methods=['GET', 'POST'])
@login_required
def user_update(user_id):
    if str(current_user.id) == (user_id):
        person = User.query.filter_by(id=user_id).first()
        if request.method == 'POST':

            person.first_name = request.form['f_name']
            person.last_name = request.form['l_name']
            person.email = request.form['email']
            db.session.commit()
            flash('Your information has been updated. Click Profile to check.',
                  category='success')

        return render_template('user_update.html', user=person)
    else:
        return render_template('post_restriction.html')


@auth.route('/profile/<user_id>/delete', methods=['GET', 'POST'])
@login_required
def user_delete(user_id):
    if str(current_user.id) == (user_id):
        person = User.query.filter_by(id=user_id).first()
        person_post = Post.query.filter_by(poster_id=user_id).all()
        for post in person_post:
            post_like = Like.query.filter_by(post_id=post.id).all()
            for row in post_like:
                db.session.delete(row)
                db.session.commit()
            post_comment = Comment.query.filter_by(post_id=post.id).all()
            for row in post_comment:
                db.session.delete(row)
                db.session.commit()
            db.session.delete(post)
            db.session.commit()
        person_like = Like.query.filter_by(user_id=user_id).all()
        for row in person_like:
            db.session.delete(row)
            db.session.commit()
        person_comment = Comment.query.filter_by(user_id=user_id).all()
        for row in person_comment:
            db.session.delete(row)
            db.session.commit()
        logout_user()
        db.session.delete(person)
        db.session.commit()
        flash('Account deleted successfully.')
        return redirect(url_for('auth.login'))
    else:
        return render_template('post_restriction.html')
