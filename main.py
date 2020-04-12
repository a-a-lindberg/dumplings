import datetime
import os

from flask import render_template, Flask, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import redirect, secure_filename

from config import Config
from data import db_session
from data.group import Group
from data.posts import Post
from data.users import User
from form.login import LoginForm
from form.post import PostForm
from form.register import RegisterForm

app = Flask(__name__)
app.config.from_object(Config)


login_manager = LoginManager()
login_manager.init_app(app)


#  Upload files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def main():
    db_session.global_init("db/users.sqlite")
    app.run()


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


@app.route('/user')
def user_profile():
    return render_template('profile_user.html', title='You')


@app.route('/group', methods=['GET', 'POST'])
def group():
    session = db_session.create_session()
    form = PostForm()
    if form.validate_on_submit():
        file = form.file_url.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            way_to_file = os.path.join(app.config['UPLOAD_FOLDER_GROUP'], filename)
            file.save(way_to_file)
        post = Post(text=form.text.data,
                    date=datetime.datetime.now().strftime("%A %d %b %Y (%H:%M %Z)"),
                    autor_id=1,
                    file=way_to_file)
        session.add(post)
        session.commit()
        return redirect('/group')
    posts = session.query(Post).filter(Post.autor_id == 1)
    return render_template('group.html', title='Авторизация', form=form, posts=posts)


@app.route('/makegroup')
def make_group():
    return render_template('group.html', title='you')


@app.route('/group/<int:id_group>')
def edit_group(id_group):
    return render_template('group.html', title='group edit')


if __name__ == '__main__':
    main()