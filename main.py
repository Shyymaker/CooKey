import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, session, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash

# конфігурація
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'kdfkallKFLKSj40129iljdkasd39291'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Допоміжна фукнція для створення таблиць БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''З'єднання з БД, якщо воно ще не встановлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


dbase = None


@app.before_request
def before_request():
    """Встановлення з'єднання з БД перед виконанням запросу"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закриваємо з'єднання з БД, якщо воно було встановлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Сторінку не знайдено", menu=dbase.getMenu())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Помилка при додаванні статі', category='error')
            else:
                flash('Стаття успішно додана', category='success')
        else:
            flash('Помилка при додаванні статі', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Додавання статті")


@app.route("/post/<int:id_post>")
def showPost(id_post):
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/login")
def login():
    return render_template("login.html", menu=dbase.getMenu(), title="Авторизація")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Ви успішно зареєструвались!", "success")
                return redirect(url_for('login'))
            else:
                flash("Помилка при додаванні у БД", "error")
        else:
            flash("Неправильно заповнені поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Реєстрація")


if __name__ == "__main__":
    app.run(debug=True)
