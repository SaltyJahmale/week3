from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
# from flask_bootstrap import Bootstrap
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Length, DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdasdqweqwezxczsc213123123qweqwe123'
# Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\dewijones\PycharmProjects\week3\data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
my_choices = [('Green', 'Green'), ('Blue', 'Blue'), ('Yellow', 'Yellow'), ('Red', 'Red')]

app_mode = "safe"
# app_mode = "unsafe"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    address = db.Column(db.String(64), unique=False, nullable=False)
    color = db.Column(db.String(64), unique=False, nullable=True)

def __repr__(self):
    return '<User %r>' % self.username

class QuestionForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=64)])
    address = StringField('Address', validators=[InputRequired(), Length(min=4, max=64)])

class ColorForm(FlaskForm):
    color = SelectField(u'Color', choices=my_choices, validators=[DataRequired()])

@app.route('/', methods=['GET','POST'])
def name_address_form():
    form = QuestionForm()
    conn = sqlite3.connect('data.db')

    # result = db.engine.execute("SELECT * FROM users")
    # print(result)
    # SQL injection
    # Malicious code injection
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(username = form.username.data).first()
            if user is None:
                user = User(username = form.username.data, address = form.address.data)
                db.session.add(user)
                db.session.commit()
                session['username'] = form.username.data
                session['address'] = form.address.data
                return redirect(url_for('color_form'))
            else:
                return redirect(url_for('color_form'))
        else:
            flash('Username and Address has a length of min 4')

    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.execute(users_query)
    list_of_users = []
    for user_query in users:
        list_of_users.append(user_query)

    return render_template('index.html', form=form, users=list_of_users)

@app.route('/color_question', methods=['GET','POST'])
def color_form():
    form = ColorForm()
    conn = sqlite3.connect('data.db')

    if request.method == 'POST':
        session['fav_color'] = form.color.data
        username = session.get('username')
        user = User.query.filter_by(username=username).first()

        if user is not None:
            user.color = session.get('fav_color')
            db.session.commit()
            return redirect(url_for('show_thanks'))
        else:
            flash('User with the username could not be found!')

    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.execute(users_query)
    list_of_users = []
    for user_query in users:
        list_of_users.append(user_query)

    return render_template('question2.html', username=session.get('username'), form=form, users=list_of_users)

@app.route('/show_thanks')
def show_thanks():
    conn = sqlite3.connect('data.db')

    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.execute(users_query)
    list_of_users = []
    for user_query in users:
        list_of_users.append(user_query)

    return render_template('show.html', username=session.get('username'), color=session.get('fav_color'), users=list_of_users)

#####################################################################################################################

@app.route('/unsafe_index', methods=['GET','POST'])
def unsafe_name_address_form():
    conn = sqlite3.connect('data.db')

    if request.method == 'POST':
        # SQL injection
        # Example: create table and execute
        # asd'; DROP TABLE table_name --
        query = "SELECT username FROM users WHERE username = '" + request.form['unsafe_username'] + "'"
        print(query)
        user_query = conn.executescript(query)

        result = None
        for username in user_query:
            result = username[0]

        if result is None:
            # SQL injection
            conn = sqlite3.connect('data.db')
            print("Opened database successfully")
            sql_string = "INSERT INTO users (username, address) VALUES ('" + request.form['unsafe_username'] + "', '" + request.form['unsafe_address'] + "')"
            conn.executescript(sql_string)
            conn.commit()
            session['unsafe_username'] = request.form['unsafe_username']
            # session['address'] = form.address.data
            return redirect(url_for('unsafe_color_form'))
        else:
            session['unsafe_username'] = request.form['unsafe_username']
            return redirect(url_for('unsafe_color_form'))

    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.execute(users_query)
    list_of_users = []
    for user_query in users:
        list_of_users.append(user_query)

    return render_template('unsafe_index.html', users=list_of_users)

@app.route('/unsafe_color_question', methods=['GET','POST'])
def unsafe_color_form():
    conn = sqlite3.connect('data.db')

    if request.method == 'POST':
        session['unsafe_fav_color'] = request.form['unsafe_fav_color']

        # SQL injection
        print("Opened database successfully")
        query = "SELECT username FROM users WHERE username = '" + session.get('unsafe_username') + "'"
        user_query = conn.executescript(query)

        result = None
        for username in user_query:
            result = username[0]

        if result is not None:
            sql_string = " UPDATE users SET color = ('" + request.form['unsafe_fav_color'] + "') WHERE username = '" + session.get('unsafe_username') + "'"
            conn.executescript(sql_string)
            conn.commit()
            return redirect(url_for('unsafe_show_thanks'))

        else:
            flash('User with the username could not be found!')

    # users = User.query.all()
    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.executescript(users_query)

    list_of_users = []
    for user_query in users:
        list_of_users.append(user_query)

    return render_template('unsafe_question2.html', username=session.get('unsafe_username'), users=list_of_users)

@app.route('/unsafe_show_thanks')
def unsafe_show_thanks():

    conn = sqlite3.connect('data.db')
    users_query = "SELECT * FROM users ORDER BY RANDOM() LIMIT 10"
    users = conn.executescript(users_query)

    list_of_users = []
    for user in users:
        list_of_users.append(user)

    return render_template('unsafe_show.html', username=session.get('unsafe_username'), color=session.get('unsafe_fav_color'), users=list_of_users)

if __name__ == '__main__':
    app.run(debug=True)
