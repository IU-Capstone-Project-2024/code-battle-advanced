from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from pathlib import Path
import markdown
import markdown.extensions.fenced_code
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testlol'
app.config['MONGO_dbname'] = 'CBA_database'
app.config['MONGO_URI'] = 'mongodb://adminuser:password123@192.168.49.2:32000/Users?authSource=admin'
mongo = PyMongo(app)
p = Path('./tasks')
UPLOAD_FOLDER = './uploaded'


@app.route("/")
@app.route("/main")
def main():
    return render_template('index.html')


def get_number(username, task_name):
    submissions = mongo.db.submissions.find({'sender': username, 'task_name': task_name})
    if submissions is None:
        return 1
    else:
        max_try = 0
        for i in submissions:
            if i["n_try"] > max_try:
                max_try = i["n_try"]
        return max_try+1

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        signup_user = users.find_one({'username': request.form['username']})
        if signup_user is not None:
            flash(request.form['username'] + ' username is already exist')
            return redirect(url_for('signup'))
        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(14))
        users.insert_one({'username': request.form['username'], 'password': hashed, 'email': request.form['email']})
        return redirect(url_for('signin'))
    return render_template('signup.html')


@app.route('/index')
def index():
    session["listOfUrls"] = [f.parts[-1] for f in p.iterdir() if f.is_dir()]
    if 'username' in session:
        return render_template('index.html', username=session['username'], listOfUrls=session['listOfUrls'])

    return render_template('index.html')


@app.route('/<string:task_name>')
def task(task_name):
    readme_file = open(f"tasks/{task_name}/description.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )
    md_template_string += render_template('task.html', url=task_name)
    return md_template_string


@app.route('/<string:task_name>/success', methods=['POST'])
def success(task_name):
    if request.method == 'POST':
        number = get_number(session["username"], task_name)
        f = request.files['file']
        ext = os.path.splitext(f.filename)[-1]
        name = f.filename
        filename = str(uuid.uuid4()) + ext
        f.save(f"uploaded/{filename}")
        mongo.db.submissions.insert_one({'sender': session['username'], 'task_name': task_name, 'filename': filename, 'n_try': number, 'language':'python3', 'state': 0})
        return render_template("Acknowledgement.html", name=name)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        signin_user = users.find_one({'username': request.form['username']})

        if signin_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), signin_user['password']) == \
                    signin_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        flash('Username and password combination is wrong')
        return render_template('signin.html')

    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
