import sqlite3
import os
from flask import Flask, render_template, request, g, abort, flash, session, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from generator import generator

# конфігурація
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'kdfkallKFLKSj40129iljdkasd39291'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступу до закритих сторінок!"
login_manager.login_message_category = "error"
name = 0
original = ""


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


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
    return render_template('index.html', menu=dbase.getMenu())


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


@app.route("/my_psw", methods=["POST", "GET"])
@login_required
def addPsw():
    global original
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['psw']) > 10:
            original = request.form['psw']
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addPsw(current_user.get_id(), request.form['name'], hash)
            if not res:
                flash('Помилка збереження паролю', category='error')
            else:
                flash('Пароль успішно доданий', category='success')
        else:
            flash('Помилка збереження статті', category='error')

    return render_template('my_psw.html', menu=dbase.getMenu(), title="Збереження паролів")


@app.route("/psw/<int:id_psw>")
@login_required
def showPsw(id_psw):
    title, psw = dbase.getPsw(id_psw)
    psw = original
    if not title:
        abort(404)

    return render_template('psw.html', menu=dbase.getMenu(), title=title, psw=psw)


@app.route("/about_us")
def about():
    return render_template('about_us.html', menu=dbase.getMenu(), title="Про нас")


@app.route("/contact")
def contact():
    return render_template('contact.html', menu=dbase.getMenu(), title="Зворотній зв'язок")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неправильна пара логін/пароль", "error")

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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з облікового запису ", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu(), title="Мій профіль", passwords=dbase.getPswAnonce(current_user.get_id()))


@app.route("/generator", methods=["POST", "GET"])
def generation():
    global name
    if request.method == "POST":
        length = int(request.form.get('name'))
        if length >= 5 and length <= 20:
            if request.form.get('sym') == '+':
                name = generator.generate(length, symbols=True, uppercase=False)
            if request.form.get('upper') == '+':
                name = generator.generate(length, symbols=False, uppercase=True)
            if request.form.get('sym') == '+' and request.form.get('upper') == '+':
                name = generator.generate(length, symbols=True, uppercase=True)
            if request.form.get('sym') != '+' and request.form.get('upper') != '+':
                name = generator.generate(length, symbols=False, uppercase=False)
        else:
            flash("Допустима довжина паролю від 5 до 20!", "error")

    return render_template("generator.html", menu=dbase.getMenu(), title="Генератор паролів", name=name)


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Помилка обновлення аватарки", "error")
                flash("Аватар обновлений", "success")
            except FileNotFoundError as e:
                flash("Помилка зчитування файлу", "error")
        else:
            flash("Помилка обновлення аватарки", "error")

    return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)
