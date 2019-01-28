from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def name_address_form():
    username = request.form['username']
    return redirect( url_for('.render_color_form', username=username))

@app.route('/color_question/')
def render_color_form():
    return render_template('question2.html', username=request.args.get('username'))

@app.route('/color_question/', methods=['POST'])
def color_form():
    color = request.form['fav_color']
    username1 = request.args.get('username')

    return redirect( url_for('.show_thanks', username=username1, color=color))

@app.route('/show_thanks/')
def show_thanks():
    return render_template('show.html', username=request.args.get('username'), color=request.args.get('color'))


if __name__ == '__main__':
    app.run(debug=True)
