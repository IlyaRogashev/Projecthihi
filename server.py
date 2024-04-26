import os

from flask import Flask, render_template, request, redirect, g, flash, abort
from data import db_session
from data.loginform import LoginForm
from data.posts import Posts
from data.users import User
from forms.post import PForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['FILE_FOLDER'] = 'static/img'


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(Posts).all()
    for i in news:
        print(i)
    return render_template("index.html", posts=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('reg.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = PForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = Posts()
        news.title = form.title.data
        print(form.file.data)
        form.file.data.save(os.path.join(app.config['FILE_FOLDER'], form.file.data.filename))
        if form.file.data:
            news.file = f'static/img/{form.file.data.filename}'
        current_user.post.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = PForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(Posts).filter(Posts.id == id,
                                           Posts.user == current_user
                                           ).first()
        if news:
            form.title.data = news.title
            news.title = form.title.data

        else:
            abort(404)
    if form.validate_on_submit():

        db_sess = db_session.create_session()
        news = db_sess.query(Posts).filter(Posts.id == id,
                                           Posts.user == current_user
                                           ).first()
        if news:
            news.title = form.title.data
            if form.file.data:
                news.file = f'static/img/{form.file.data.filename}'
                form.file.data.save(os.path.join(app.config['FILE_FOLDER'], form.file.data.filename))
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('posts.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Posts).filter(Posts.id == id,
                                       Posts.user == current_user
                                       ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')
@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    db_session.global_init("db/blogs.db")
    app.run('127.0.0.1', port=8300, debug=True)
