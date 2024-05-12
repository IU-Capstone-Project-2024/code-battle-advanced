from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from pathlib import Path
import markdown
import markdown.extensions.fenced_code
import uuid
import os
from datetime import datetime, timezone, timedelta
from zipfile import ZipFile
import math
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testlol'
app.config['MONGO_dbname'] = 'CBA_database'
app.config['MONGO_URI'] = 'mongodb://adminuser:password123@192.168.49.2:32000/CBA_database?authSource=admin'
mongo = PyMongo(app)
p = Path('./tasks')
UPLOAD_FOLDER = './submissions'
redis_host = "redis"


@app.route("/")
@app.route("/main")
def main():
    return render_template('index.html')


def get_number(username, task_name):
    submissions_array = mongo.db.submissions.find({'sender': username, 'task_name': task_name})
    if submissions_array is None:
        return 1
    else:
        max_try = 0
        for i in submissions_array:
            if i["n_try"] > max_try:
                max_try = i["n_try"]
        return max_try + 1


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        signup_user = users.find_one({'username': request.form['username']})
        if signup_user is not None:
            flash(request.form['username'] + ' username is already exist')
            return redirect(url_for('signup'))
        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(14))
        users.insert_one(
            {'username': request.form['username'], 'password': hashed, 'email': request.form['email'], 'admin': False})
        return redirect(url_for('signin'))
    return render_template('signup.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        if request.method == 'POST':
            mongo.db.contests.insert_one({'name': request.form['ContestName'], 'tasks': [],
                                          'duration': request.form['duration'],
                                          'startTime': datetime.strptime(request.form['StartTime'],
                                                                         "%d/%m/%Y %H:%M:%S")})
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        session["contests"] = [i['name'] for i in mongo.db.contests.find()
                               if (i['startTime'].replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) <=
                                   i['startTime'].replace(tzinfo=timezone.utc)
                                   + timedelta(minutes=int(i['duration']))) or (admin and datetime.now(timezone.utc) <=
                                                                                i['startTime'].replace(
                                                                                    tzinfo=timezone.utc))]
        contest_archive = [i for i in mongo.db.contests.find()
                           if i['name'] not in session['contests'] and datetime.now(timezone.utc) >
                           i['startTime'].replace(tzinfo=timezone.utc)
                           + timedelta(minutes=int(i['duration']))]
        tasks_archive = []
        for i in contest_archive:
            tasks_archive += [(i['name'], j, mongo.db.tasks.find_one({'uuid': j})['task_name']) for j in i['tasks']]
        if len(tasks_archive) == 0:
            return render_template('index.html', username=session['username'],
                                   listOfUrls=session['contests'], admin=admin)
        return render_template('index.html', username=session['username'],
                               listOfUrls=session['contests'], admin=admin, all_tasks=tasks_archive)
    return render_template('index.html')


@app.route('/contest/<string:contest_name>', methods=['GET', 'POST'])
def contest(contest_name):
    my_contest = mongo.db.contests.find_one({"name": contest_name})
    admin = mongo.db.users.find_one({'username': session['username']})['admin']
    if (not my_contest['startTime'].replace(tzinfo=timezone.utc)
            <= datetime.now(timezone.utc) <= my_contest['startTime'].replace(tzinfo=timezone.utc)
            + timedelta(minutes=int(my_contest['duration']))) and not admin:
        print(admin)
        return render_template("error.html")
    if 'username' not in session:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        f = request.files['zip']
        zip_handle = ZipFile(f._file)
        for info in zip_handle.infolist():
            zip_handle.extract(info.filename, "tasks/")
        for info in zip_handle.infolist():
            if info.is_dir() and info.filename.count("/") == 1:
                filename = str(uuid.uuid4())
                task_name = info.filename
                os.rename("tasks/" + info.filename, "tasks/" + filename)
                task_name = task_name.split("/")[0]
                if task_name not in mongo.db.contests.find_one({'name': contest_name})['tasks']:
                    mongo.db.contests.update_one({'name': contest_name}, {'$push': {'tasks': filename}})
                mongo.db.tasks.insert_one({'uuid': filename, "task_name": task_name})
    admin = mongo.db.users.find_one({'username': session['username']})['admin']
    tasks = mongo.db.contests.find_one({'name': contest_name})["tasks"]
    print(tasks)
    tasks = [(mongo.db.tasks.find_one({'uuid': i})["task_name"], i) for i in tasks]
    if 'username' in session:
        return render_template('contest.html', admin=admin,
                               listOfTasks=tasks, contest_name=contest_name, username=session['username'])
    else:
        return render_template('contest.html', listOfTasks=tasks, contest_name=contest_name,
                               username=session['username'])


@app.route('/task/<string:task_name>')
def task(task_name):
    if 'username' not in session:
        return render_template('unauthorized.html')
    readme_file = open(f"tasks/{task_name}/description.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )
    md_template_string += render_template('task.html', url=task_name, username=session['username'])
    return md_template_string


@app.route('/contest/<string:contest_name>/task/<string:task_name>')
def contest_task(contest_name, task_name):
    if 'username' not in session:
        return render_template('unauthorized.html')
    readme_file = open(f"tasks/{task_name}/description.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )
    md_template_string += render_template('task.html', url=task_name, username=session['username'],
                                          contest_name=contest_name)
    return md_template_string


def success_support_func(task_name):
    languages = {"Python 3.19": "python3", "C++ 17": "cpp"}
    language = request.form['language']
    number = get_number(session["username"], task_name)
    f = request.files['file']
    filename = str(uuid.uuid4())
    f.save(f"submissions/{filename}")
    return filename, number, languages[language]


@app.route('/contest/<string:contest_name>/task/<string:task_name>/success', methods=['POST'])
def contest_success(contest_name, task_name):
    if request.method == 'POST':
        f, n, lang = success_support_func(task_name)
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        my_contest = mongo.db.contests.find_one({"name": contest_name})
        if (not (my_contest['startTime'].replace(tzinfo=timezone.utc)
                 <= datetime.now(timezone.utc) <= my_contest['startTime'].replace(tzinfo=timezone.utc)
                 + timedelta(minutes=int(my_contest['duration'])))) and not admin:
            return render_template("error.html")
        _id = mongo.db.submissions.insert_one({'sender': session['username'],
                                               "datetime in UTC": datetime.now(timezone.utc),
                                               'task_name': task_name,
                                               'in_contest_name': mongo.db.tasks.find_one({"uuid":
                                                                                               task_name})["task_name"],
                                               'filename': f, 'n_try': n,
                                               'language': lang,
                                               'contest': contest_name,
                                               'verdict': "N/A"}).inserted_id
        if type(_id) != str:
            _id = str(_id)
        q.lpush("job2", _id + ":3")
        return render_template("acknowledgement.html")


@app.route('/task/<string:task_name>/success', methods=['POST'])
def success(task_name):
    if request.method == 'POST':
        f, n, lang = success_support_func(task_name)
        success_support_func(task_name)
        _id = mongo.db.submissions.insert_one({'sender': session['username'],
                                               "datetime in UTC": datetime.now(timezone.utc),
                                               'task_name': task_name,
                                               'in_contest_name': mongo.db.tasks.find_one({"uuid":
                                                                                               task_name})["task_name"],
                                               'filename': f, 'n_try': n,
                                               'language': lang,
                                               'contest': 'No contest',
                                               'verdict': "N/A"}).inserted_id
        if type(_id) != str:
            _id = str(_id)
        q.lpush("job2", _id + ":3")
        return render_template("acknowledgement.html")


def get_string_submissions(submissions_arr):
    result = []
    for i in submissions_arr:
        result.append(f"time: {i['datetime in UTC']}; contest: {i['contest']}; task_name: {i['in_contest_name']};"
                      f" language: {i['language']}; verdict: {i['verdict']}")
    return result


@app.route('/submissions/<int:page_number>', methods=['POST', 'GET'])
def submissions(page_number):
    submissions_array = mongo.db.submissions.find({'sender': session['username']})
    submissions_array = sorted(submissions_array, key=lambda x: x['datetime in UTC'], reverse=True)
    limit_page = min(math.ceil(len(submissions_array) / 10), 1)
    submissions_array = submissions_array[(page_number - 1) * 10:page_number * 10]
    return render_template("submissions.html",
                           submissions_array=get_string_submissions(submissions_array), current_page=page_number,
                           limit_page=limit_page)


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
    q = redis.StrictRedis(host=redis_host)
    app.run(host='0.0.0.0', debug=True)
