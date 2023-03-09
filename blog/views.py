from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from flask import current_app as app
import uuid
from . import db
from sqlalchemy import func
from .models import Post, User, Follow, Comment, Like
import csv

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    users = User.query
    users = users.order_by(func.random()).limit(3)

    posts = Post.query.join(Follow, Follow.followed_id == Post.poster_id).filter(
        Follow.follower_id == current_user.id)

    return render_template("index_blog.html", posts=posts, user=current_user, users=users)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users = User.query.all()
    profile_image = url_for('static',
                            filename='profile_pics/' + current_user.profile_pic)

    posts = current_user.posts
    count = 0
    for post in posts:
        count += 1
    return render_template("profile.html", posts=posts, count=count, users=users, user=current_user, profile_image=profile_image)


@views.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def other_profile(username):
    users = User.query.all()
    if current_user.username != username:
        user = User.query.filter_by(username=username).first_or_404()
        follows_user = None
        if User.is_following(current_user, user) == True:
            follows_user = True
        else:
            follows_user = False
        posts = user.posts
        count = 0
        for post in posts:
            count += 1
        profile_image = url_for('static',
                                filename='profile_pics/' + user.profile_pic)

        posts = user.posts
        return render_template("other_profile.html", users=users, follows_user=follows_user, user=user, count=count, posts=posts, profile_image=profile_image)
    else:
        return redirect(url_for('views.profile'))


@views.route('/post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        blog_title = request.form.get('blog_title')
        blog_description = request.form.get('blog_description')
        blog_pic = request.files['blog_pic']
        poster = current_user.id

        if blog_pic:

            blog_pic_name = secure_filename(blog_pic.filename)
            blog_picture_name = str(uuid.uuid1())+"__" + blog_pic_name
            blog_pic.save(os.path.join(
                app.root_path, 'static\\blog_pics', blog_picture_name))

        else:
            blog_picture_name = ""
        new_post = Post(title=blog_title,
                        description=blog_description, image=blog_picture_name, poster_id=poster)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created.', category='success')
    return render_template('new_post.html')


@views.route('/post/<postid>,<username>/update', methods=['GET', 'POST'])
@login_required
def update_post(postid, username):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=postid).first_or_404()
    if request.method == 'POST':
        if user == current_user and post.poster_id == current_user.id:

            post.blog_pic = request.files['blog_pic']

            if post.blog_pic:

                blog_pic_name = secure_filename(post.blog_pic.filename)
                blog_picture_name = str(uuid.uuid1())+"__" + blog_pic_name
                post.blog_pic.save(os.path.join(
                    app.root_path, 'static\\blog_pics', blog_picture_name))

            else:
                blog_picture_name = ""
            post.image = blog_picture_name
            post.title = request.form.get('blog_title', post.title)
            post.description = request.form.get(
                'blog_description', post.description)
            db.session.commit()
            flash('Your post has been updated.', category='success')
            return render_template('post_updated.html', post=post)
        else:
            return render_template('post_restriction.html')

    else:
        return render_template('post_updated.html', post=post)


@views.route('/post/<postid>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(postid):

    post = Post.query.filter_by(id=postid).first_or_404()
    if post.poster_id == current_user.id:
        person_like = Like.query.filter_by(post_id=postid).all()
        person_comment = Comment.query.filter_by(post_id=postid).all()
        for row in person_like:
            db.session.delete(row)
            db.session.commit()
        for row in person_comment:
            db.session.delete(row)
            db.session.commit()

        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted.', category='success')
        return redirect(url_for('views.profile'))
    else:
        return render_template('post_restriction.html')


@views.route('/posts/<postid>,<username>', methods=['GET', 'POST'])
@login_required
def posts(postid, username):
    comments = Comment.query.filter_by(post_id=postid).all()
    likes = Like.query.filter_by(post_id=postid).all()
    l_count = 0
    for like in likes:
        l_count += 1
    user = User.query.filter_by(username=username).first_or_404()
    c_count = 0
    for comment in comments:
        c_count += 1

    if request.method == 'POST':

        comment = request.form['comment']
        post_id = postid
        user_id = current_user.id
        new_comment = Comment(
            comment=comment, post_id=post_id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
        comments = Comment.query.filter_by(post_id=postid).all()
        c_count = 0
        for comment in comments:
            c_count += 1
        post = Post.query.filter_by(id=postid).first_or_404()

        return render_template('posts.html', post=post, comments=comments, count=c_count, l_count=l_count)

    if User.is_following(current_user, user) == True or user == current_user:
        post = Post.query.filter_by(id=postid).first_or_404()

        return render_template('posts.html', post=post, comments=comments, count=c_count, l_count=l_count)
    else:
        return render_template('post_restriction.html')


@views.route('/search', methods=["GET", "POST"])
@login_required
def search():
    if request.method == 'POST':
        key = request.form['key']
        users = User.query
        users = users.filter(User.username.like(key+'%')).all()
        no_match = None
        if users == None:
            no_match == 1
        else:
            users = users
        return render_template('search.html', users=users, no_match=no_match, current_user=current_user, key=key)
    else:
        return render_template('search.html')


@views.route('/posts/<postid>,<username>/like')
@login_required
def like(postid, username):
    post = Post.query.filter_by(id=postid).first()
    user = User.query.filter_by(username=username).first()
    if post is None:
        flash('No post found with username {}.'.format(
            username), category='warning')
        return redirect(url_for('views.home'))

    current_user.like(post)
    db.session.commit()
    return redirect(url_for('views.posts', postid=postid, username=username))


@views.route('/posts/<postid>,<username>/unlike')
@login_required
def unlike(postid, username):
    post = Post.query.filter_by(id=postid).first()
    user = User.query.filter_by(username=username).first()
    if post is None:
        flash('No post found with username {}.'.format(
            username), category='warning')
        return redirect(url_for('views.home'))

    current_user.unlike(post)
    db.session.commit()
    return redirect(url_for('views.posts', postid=postid, username=username))


@views.route('/post/<postid>,<username>/export', methods=['GET', 'POST'])
def export_data(postid, username):
    comments = Comment.query.filter_by(post_id=postid).all()
    likes = Like.query.filter_by(post_id=postid).all()
    l_count = 0
    for like in likes:
        l_count += 1
    user = User.query.filter_by(username=username).first_or_404()
    c_count = 0
    for comment in comments:
        c_count += 1

    post = Post.query.filter_by(id=postid).first_or_404()
    post_title = post.title
    person = User.query.filter_by(username=username).first_or_404()
    f = open(os.path.join(
        app.root_path, 'static\\downloaded_blogs\\' + post_title + '.csv'), 'w')
    csvwriter = csv.writer(f)
    csvwriter.writerow(["First name", "Username", "email id",
                        "Post Title", "Post Caption", "Like Count", "Comment Count"])
    csvwriter.writerow([person.first_name, person.username,
                        person.email, post.title, post.description, l_count, c_count])
    f.close()
    flash('Data has been exported successfully in "blog\static\downloaded_blogs" folder with title name', category='success')
    return redirect(url_for('views.posts', postid=postid, username=username))
