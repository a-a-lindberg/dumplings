import datetime
import os
import requests
import json
import random

from flask_login import AnonymousUserMixin
from flask import render_template, Flask, request, flash, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect, secure_filename

from config import Config
from data import db_session
from data.group import Group
from data.posts import Post
from data.user_posts import PostUser
from data.users import User
from form.edit_group import GhangeIngoForm
from form.login import LoginForm
from form.post import PostForm
from form.register import RegisterForm
from form.edit import EditForm
from form.delete import DeleteForm

app = Flask(__name__)
app.config.from_object(Config)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.id = '0'


login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.init_app(app)


#  Upload files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def main():
    db_session.global_init("db/users.sqlite")
    app.run()


@app.before_request
def before_request():
    g.user = current_user


@app.route('/game/<id>', methods=['GET', 'POST'])
def game(id):
    return render_template("game.html", id=id)


@app.route('/apps')
def apps():
    return render_template("apps.html")


@app.route("/")
def index():
    return render_template("base.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    form = DeleteForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('delete.html', title='Deletion',
                                   form=form,
                                   message="Пароли не совпадают")
        else:
            session = db_session.create_session()
            my = g.user.id
            user = session.query(User).filter(User.id == my).first()
            if user.check_password(form.password.data):
                session.delete(user)
                session.commit()
                return redirect('/register')
    return render_template('delete.html', title='Deletion', form=form)


@app.route('/user/<id>', methods=['GET', 'POST'])
def user_profile(id):
    session = db_session.create_session()
    user = session.query(User).filter_by(id=id).first()
    form = PostForm()
    if user == None:
        flash('User ' + id + ' not found.')
        return render_template('login.html')
    else:
        you = user.name
        my = g.user.id
        info = user.about
        user_id = int(id)
        if my == user_id:
            if form.validate_on_submit():
                file = form.file_url.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    way_to_file = os.path.join(app.config['UPLOAD_FOLDER_USER'], filename)
                    file.save(way_to_file)
                    post = PostUser(text=form.text.data,
                                date=datetime.datetime.now().strftime("%A %d %b %Y (%H:%M %Z)"),
                                autor_id=my,
                                file=way_to_file)
                    session.add(post)
                    session.commit()
                    return redirect(f'{id}')
                elif file.filename == '':
                    post = PostUser(text=form.text.data,
                                date=datetime.datetime.now().strftime("%A %d %b %Y (%H:%M %Z)"),
                                autor_id=my)
                    session.add(post)
                    session.commit()
                    return redirect(f'{id}')
            posts = session.query(PostUser).filter_by(autor_id=user_id).order_by(PostUser.id.desc())
            return render_template('profile_user.html', title=you, you=you, user_id=user_id, my_id=my, info=info,
                                   form=form, posts=posts)
        else:
            posts = session.query(PostUser).filter_by(autor_id=user_id).order_by(PostUser.id.desc())
            return render_template('profile_user.html', title=you, you=you, user_id=user_id, my_id=my, info=info,
                                   form=form, posts=posts)


@app.route('/post_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def post_edit(id):
    form = PostForm()
    session = db_session.create_session()
    post = session.query(Post).filter_by(id=id).first()
    prev_text = post.text
    my = g.user.id
    if request.method == 'POST':
        new_text = request.form.get("area")
        file = form.file_url.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            way_to_file = os.path.join(app.config['UPLOAD_FOLDER_USER'], filename)
            file.save(way_to_file)
            post.text = new_text
            session.commit()
            return redirect(f'/user/{g.user.id}')
        elif file.filename == '':
            post.text = new_text
            session.commit()
            return redirect(f'/user/{g.user.id}')
    return render_template('delete_post.html', form=form, prev_text=prev_text)


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    session = db_session.create_session()
    news = session.query(Post).filter(Post.id == id,
                                      Post.autor_id == g.user.id).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        os.abort(404)
    return redirect(f'/user/{g.user.id}')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user_id = g.user.id
        user = session.query(User).filter_by(id=int(user_id)).first()
        user.about = form.about_me.data
        session.commit()
        flash('Your changes have been saved.')
        return redirect(f'user/{user_id}')
    else:
        session = db_session.create_session()
        user_id = g.user.id
        user = session.query(User).filter_by(id=int(user_id)).first()
        form.about_me.data = user.about
    return render_template('edit.html',
                           form=form)


@app.route('/group/<int:id_group>', methods=['GET', 'POST'])
def group(id_group):
    session = db_session.create_session()
    form = PostForm()
    if form.validate_on_submit():
        way_to_file = ""
        file = form.file_url.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            way_to_file = os.path.join(app.config['UPLOAD_FOLDER_GROUP'], filename)
            file.save(way_to_file)
        post = Post(text=form.text.data,
                    date=datetime.datetime.now().strftime("%A %d %b %Y (%H:%M)"),
                    autor_id=id_group,
                    file=way_to_file)
        session.add(post)
        session.commit()
        return redirect(f'/group/{id_group}')
    posts = session.query(Post).filter(Post.autor_id == id_group)
    return render_template('group.html', title='Авторизация', form=form, posts=posts)


@app.route('/makegroup')
def make_group():
    return render_template('group.html', title='you')


@app.route('/group/<int:id_group>/edit')
def edit_group(id_group):
    form = GhangeIngoForm()
    if request.method == "GET":
        session = db_session.create_session()
        group = session.query(Group).filter(Group.id == id_group).first()
        if group:
            form.name.data = group.name
            form.info.data = group.info
        else:
            os.abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        group = session.query(Group).filter(Group.id == id_group).first()
        if group:
            form.name.data = group.name
            form.info.data = group.info
            session.commit()
            return redirect('/group')
        else:
            os.abort(404)
    return render_template('edit.html',
                           form=form)


@app.route('/joke')
def random_joke():
    api_server = "https://icanhazdadjoke.com/slack"
    response = requests.get(api_server)
    json_response = response.json(strict=False)
    picture = json_response["attachments"][0]["text"]
    num = random.randint(1, 21)
    name = "img/laugh/laugh" + str(num) + ".jpg"
    return render_template("joke.html", joke=picture, name=name)

if __name__ == '__main__':
    main()