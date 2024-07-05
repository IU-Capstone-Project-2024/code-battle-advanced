from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from pathlib import Path
import markdown
import markdown.extensions.fenced_code
import uuid
import os
from datetime import datetime, timezone, timedelta
import math
import pytz
import shutil
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testlol'
app.config['MONGO_dbname'] = 'Users'
app.config[
    'MONGO_URI'] = f"mongodb://{os.environ['MONGO_INITDB_ROOT_USERNAME']}:{os.environ['MONGO_INITDB_ROOT_PASSWORD']}@192.168.49.2:32000/CBA_database?authSource=admin"
mongo = PyMongo(app)
p = Path('./tasks')
UPLOAD_FOLDER = './submissions'
redis_host = "redis"


@app.route("/")
@app.route("/main")
def main():
    if 'username' in session:
        session.pop('username')
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
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        return render_template('index.html', username=session['username'], admin=admin)
    return render_template('index.html')


def return_bson(name):
    uploaded_files = request.files.getlist(name)
    bson_documents = []
    for i in uploaded_files:
        filename = i.filename
        file_data = i.read()
        bson_documents.append({
            'filename': filename,
            'file_data': bson.Binary(file_data)
        })
    return bson_documents


def error(admin, my_contest):
    start_time = pytz.utc.localize(my_contest['startTime'])
    if (not start_time
            <= datetime.now(pytz.utc) <= start_time
            + timedelta(minutes=int(my_contest['duration'])) and not (admin and start_time > datetime.now(pytz.utc))):
        return True
    return False


@app.route('/contest/<string:contest_name>', methods=['GET', 'POST'])
def contest(contest_name):
    my_contest = mongo.db.contests.find_one({"name": contest_name})
    admin = mongo.db.users.find_one({'username': session['username']})['admin']
    widgets = list(mongo.db.participants.find({'contest_id': contest_name, 'participant_id': session['username']}))
    name, text = None, None
    has_widgets = len(widgets) > 0
    if len(widgets) > 0:
        name, text = [i.lstrip("TextWidget(\'").rstrip("\'").split('\' ,') for i in widgets]
    if error(admin, my_contest):
        return render_template('error.html')
    if 'username' not in session:
        return render_template('unauthorized.html')
    admin = mongo.db.users.find_one({'username': session['username']})['admin']

    if request.method == 'POST':
        filename = str(uuid.uuid4())
        available_languages = [i if request.form[i] else None for i in ['py', 'java', 'cpp']]
        md = return_bson('md-file')[0]
        if 'input-file' in request.files and 'checker-file' in request.files:
            input1 = return_bson('input-file')
            checker = return_bson('checker-file')
            mongo.db.tasks.insert_one({'uuid': filename, "task_name": request.form['name'],
                                       "input": input1,
                                       "checker": checker,
                                       "judgement_mod": request.form["judgement_mod"],
                                       "available": available_languages,
                                       "tags": request.form['tags'].split(","),
                                       'md': md})
        elif 'input-file' in request.files and 'solution-file' in request.files:
            input1 = return_bson('input-file')
            solution = return_bson('solution-file')
            mongo.db.tasks.insert_one({'uuid': filename, "task_name": request.form['name'],
                                       "input": input1,
                                       "solution": solution,
                                       "judgement_mod": request.form["judgement_mod"],
                                       "available": available_languages,
                                       "tags": request.form['tags'].split(","),
                                       'md': md})
        elif 'input-file' in request.files and 'interactive-file' in request.files:
            input1 = return_bson('input-file')
            interactive = return_bson('interactive-file')
            mongo.db.tasks.insert_one({'uuid': filename, "task_name": request.form['name'],
                                       "input": input1,
                                       "interactive": interactive,
                                       "judgement_mod": request.form["judgement_mod"],
                                       "available": available_languages,
                                       "tags": request.form['tags'].split(","),
                                       'md': md})
        elif 'input-file' in request.files and 'output-file' in request.files:
            input1 = return_bson('input-file')
            output = return_bson('output-file')
            mongo.db.tasks.insert_one({'uuid': filename, "task_name": request.form['name'],
                                       "input": input1,
                                       "output": output,
                                       "judgement_mod": request.form["judgement_mod"],
                                       "available": available_languages,
                                       "tags": request.form['tags'].split(","),
                                       'md': md})
        if filename not in mongo.db.contests.find_one({'name': contest_name})['tasks']:
            mongo.db.contests.update_one({'name': contest_name}, {'$push': {'tasks': filename}})

    tasks = mongo.db.contests.find_one({'name': contest_name})["tasks"]
    tasks = [(mongo.db.tasks.find_one({'uuid': i})["task_name"], i) for i in tasks]
    return render_template('contest.html', admin=admin,
                           listOfTasks=tasks, contest_name=contest_name, username=session['username'],
                           widget_name=name, widget_text=text, has_widgets=has_widgets)


@app.route('/contest/<string:contest_name>/task/<string:task_name>')
@app.route('/task/<string:task_name>')
def task(contest_name=None, task_name=None):
    if 'username' not in session:
        return render_template('unauthorized.html')
    print(contest_name)
    if contest_name is None:
        result = mongo.db.tasks.find_one({"uuid": task_name})["md"]["file_data"]
    else:
        my_contest = mongo.db.contests.find_one({"name": contest_name})
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        if error(admin, my_contest):
            return render_template("error.html")

        result = mongo.db.tasks.find_one({"uuid": task_name})["md"]["file_data"]

    md_template_string = markdown.markdown(
        result.decode(), extensions=["fenced_code", 'tables']
    )

    # Copy static resources and update paths in the Markdown content
    res_dir_names = ["static", "resources", "res"]
    for i in res_dir_names:
        if os.path.exists(f"/tasks/{task_name}/{i}"):
            shutil.copytree(f"/tasks/{task_name}/{i}", "/static", dirs_exist_ok=True)
            md_template_string = md_template_string.replace(f"src=\"./{i}", "src=\"/static")

    md_template_string = render_template('task_top.html', url=task_name, username=session['username'],
                                         contest_name=contest_name) + md_template_string + render_template(
        'task_bottom.html', url=task_name, username=session['username'], contest_name=contest_name)
    return md_template_string


def success_support_func(task_name):
    languages = {"Python 3.19": "python3", "C++ 17": "cpp", "Java": "java"}
    language = request.form['language']
    number = get_number(session["username"], task_name)
    f = request.files['file']
    return f.read(), number, languages[language]


@app.route('/task/<string:task_name>/success', methods=['POST'])
@app.route('/contest/<string:contest_name>/task/<string:task_name>/success', methods=['POST'])
def contest_success(contest_name=None, task_name=None):
    if request.method == 'POST':
        src, n, lang = success_support_func(task_name)
        if contest_name is not None:
            admin = mongo.db.users.find_one({'username': session['username']})['admin']
            my_contest = mongo.db.contests.find_one({"name": contest_name})
            if error(admin, my_contest):
                return render_template("error.html")
        _id = mongo.db.submissions.insert_one({'sender': session['username'],
                                               "datetime in UTC": datetime.now(timezone.utc),
                                               'task_name': task_name,
                                               'in_contest_name':
                                                   mongo.db.tasks.find_one({"uuid": task_name})["task_name"],
                                               'source': src, 'n_try': n,
                                               'language': lang,
                                               'filename': request.files['file'].filename,
                                               'contest': 'No contest' if contest_name is None else contest_name,
                                               'verdict': "N/A",
                                               'final_verdict': "N/A"}).inserted_id
        if not isinstance(_id, str):
            _id = str(_id)
        q.lpush("job2", _id + ":3")
        return render_template("acknowledgement.html")


def get_string_submissions(submissions_arr):
    result = []
    for i in submissions_arr:
        result.append(f"time: {i['datetime in UTC']}; contest: {i['contest']}; task_name: {i['in_contest_name']};"
                      f" language: {i['language']}; verdict: {i['final_verdict']}")
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


@app.route('/create', methods=['GET', 'POST'])
def create_contest():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
    if request.method == 'POST':
        uploaded_file = request.files['type_python']
        filename = uploaded_file.filename
        file_data = uploaded_file.read()
        bson_document = {
            'filename': filename,
            'file_data': bson.Binary(file_data)
        }
        mongo.db.contests.insert_one({'name': request.form['ContestName'], 'tasks': [],
                                      'duration': request.form['duration'],
                                      'startTime': pytz.UTC.localize(datetime.strptime(request.form['StartTime'],
                                                                                       "%d/%m/%Y %H:%M:%S")),
                                      'allowed_teams': 'teams' in request.form,
                                      'config': bson_document,
                                      'new_global_events': [(0, "Start", {})],
                                      'global_events': []})

    return render_template('create.html', admin=admin)


@app.route('/contest/<string:contest_name>/upload', methods=['GET', 'POST'])
def upload(contest_name):
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
    return render_template('upload.html', admin=admin, contest_name=contest_name)


@app.route('/contest/<string:contest_name>/leaderboard/<int:page_number>', methods=['GET', 'POST'])
def leader_board(contest_name, page_number):
    board = []
    # leaders = {}
    for i in mongo.db.participants.find({'contest_id': contest_name}):
        board.append((i["participant_id"], i["points"]))

    #        if i['sender'] not in leaders.keys():
    #            leaders[i['sender']] = {}
    #
    #        res = 0
    #        for j in i['verdict'].split("\n")[:-1]:
    #            if j.split()[0] == "AC":
    #                res += 1
    #        if i['verdict'].count("\n") != 0:
    #            res /= i['verdict'].count("\n")
    #
    #        if i['task_name'] in leaders[i['sender']].keys():
    #            leaders[i['sender']][i['task_name']] = max(res, leaders[i['sender']][i['task_name']])
    #        else:
    #            leaders[i['sender']][i['task_name']] = res
    #    board = [(i, sum(list(leaders[i].values()))) for i in list(leaders.keys())]
    board = sorted(board, key=lambda k: -k[1])
    for i in range(len(board)):
        board[i] = (i + 1, board[i][0], board[i][1])
    limit_page = min(math.ceil(len(board) / 10), 1)
    board = board[(page_number - 1) * 10:page_number * 10]
    return render_template('leaderboard.html', board=[';'.join(map(str, i)) for i in board],
                           limit_page=limit_page,
                           current_page=page_number, contest_name=contest_name)


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        return render_template('personal.html', admin=admin, username=session['username'])


@app.route('/tasks_archive', methods=['GET', 'POST'])
def tasks_archive():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        session['contests'] = []
        for i in mongo.db.contests.find():
            if not error(admin, i):
                session['contests'].append(i['name'])
        contest_archive = [i for i in mongo.db.contests.find()
                           if i['name'] not in session['contests'] and datetime.now(pytz.utc) >
                           i['startTime'].astimezone(pytz.utc)
                           + timedelta(minutes=int(i['duration']))]
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        archive = []
        for i in contest_archive:
            archive += [(i['name'], j, mongo.db.tasks.find_one({'uuid': j})['task_name']) for j in i['tasks']]
        return render_template('tasks_archive.html', all_tasks=archive, admin=admin,
                               username=session['username'])


@app.route('/contests/<string:type_contests>', methods=['GET', 'POST'])
def available_contests(type_contests):
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        if not admin and type_contests == 'my':
            return render_template('unauthorized.html')
        session['contests'] = []
        for i in mongo.db.contests.find():
            start_time = pytz.utc.localize(i['startTime'])
            if not error(admin, i):
                session['contests'].append(i['name'])
        if type_contests == 'available':
            return render_template('available.html', listOfUrls=session['contests'], admin=admin,
                                   username=session['username'])
        else:
            return render_template('my_contests.html', username=session['username'],
                                   listOfUrls=session['contests'], admin=admin)


if __name__ == "__main__":
    q = redis.StrictRedis(host=redis_host)
    app.run(host='0.0.0.0', debug=True)
