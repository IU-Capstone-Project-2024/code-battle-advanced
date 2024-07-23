from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from pathlib import Path
import markdown
import markdown.extensions.fenced_code
import os
from datetime import datetime, timezone, timedelta
import math
import pytz
import shutil
import redis
import ast
import bson
import re

from replicate.exceptions import ModelError

from threading import Thread
from ai_images import process_text

import grpc

import contest_pb2 as pb2
import contest_pb2_grpc as pb2_grpc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testlol'
app.config['MONGO_dbname'] = 'Users'
app.config[
    'MONGO_URI'] = (f"mongodb://{os.environ['MONGO_INITDB_ROOT_USERNAME']}:"
                    f"{os.environ['MONGO_INITDB_ROOT_PASSWORD']}@192.168.49.2:32000/CBA_database?authSource=admin")
mongo = PyMongo(app)
p = Path('./tasks')
UPLOAD_FOLDER = './submissions'
redis_host = "redis"


def makeimage(prompt, number, task_id):
    attempts = 0

    # engineered_prompt = "You generate colorful images to accompany programming tasks. The task name is {task_name}. The task description in md format is \"{statement}\". The user wants the picture to be {prompt}."

    while 1:
        try:
            image = process_text(prompt, filemode=False)
            break
        except (RuntimeError, ModelError) as e:
            attempts += 1
            if attempts == 10:
                image = open("/static/failure.png", "rb").read()
                break
            continue

    mongo.db.tasks.update_one({"_id": task_id}, {"$set": {f"res.ai_{number}": image}})


def get_stub():
    channel = grpc.insecure_channel("192.168.49.2:32002")
    return pb2_grpc.ContestStub(channel)


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


def has_access(user, contest_1):
    print(contest_1)
    for i in contest_1['groups']:
        group_1 = mongo.db.groups.find_one({'_id': bson.ObjectId(i)})
        if user['_id'] in group_1['members']:
            return True
    return False


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        signup_user = users.find_one({'username': request.form['username']})
        if signup_user is not None:
            flash(request.form['username'] + ' username already exists')
            return redirect(url_for('signup'))
        signup_email = users.find_one({'email': request.form['email']})
        if signup_email is not None:
            flash('User with ' + request.form['email'] + ' email already exists')
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


def error(user, admin, my_contest):
    start_time = pytz.utc.localize(my_contest['startTime'])
    if not (start_time <= datetime.now(pytz.utc) <= start_time + timedelta(minutes=int(my_contest['duration']))
            and has_access(user, my_contest)) and \
            not admin:
        return True
    return False


def refresh(md_str, id_):
    c = 0
    for i in re.findall(r"!\[.*?\]\(ai_.*?\)", md_str):
        Thread(target=makeimage, args=[i.split("]")[0][2:], c, id_]).run()
        c += 1


# def get_widgets_for_page(widgets):
#    widgets_for_page = []
#
#    for i in widgets:
#        if "TextButtonWidget(\'" not in i:
#            widgets_for_page.append([False] +
#                                    i.replace("TextWidget(\'", '').replace("\')", '').split('\', \''))
#        else:
#            widgets_for_page.append([True] +
#                                    i.replace("TextButtonWidget(\'", '').replace("\')", '').split('\', \''))
#    return widgets_for_page

@app.route('/contest/<string:contest_name>', methods=['GET', 'POST'])
def contest(contest_name):
    my_contest = mongo.db.contests.find_one({"_id": bson.ObjectId(contest_name)})
    user = mongo.db.users.find_one({'username': session['username']})
    admin = user['admin']
    cur_contest_time = datetime.utcnow() - my_contest['startTime']
    cur_contest_time = int(cur_contest_time / timedelta(milliseconds=1))
    get_stub().GoToTime(pb2.GoToTimeMessage(contest_id=contest_name,
                                            participant_id=session['username'],
                                            time=cur_contest_time))

    # name, text = None, None
    # has_widgets = len(widgets) > 0
    # widgets_for_page = get_widgets_for_page(widgets)
    if error(user, admin, my_contest):
        return render_template('error.html')
    if 'username' not in session:
        return render_template('unauthorized.html')
    admin = mongo.db.users.find_one({'username': session['username']})['admin']
    _id = None
    if request.method == 'POST':
        if request.form.get('btn'):
            get_stub().HandleEvent(pb2.EventData(contest_id=contest_name,
                                                 participant_id=session['username'],
                                                 time=cur_contest_time,
                                                 caller=request.form['btn'],
                                                 data="{}"))
            pass
    widgets = mongo.db.participants.find_one({'contest_id': contest_name, 'participant_id': session['username']})[
        'widgets']
    tasks = mongo.db.contests.find_one({'_id': bson.ObjectId(contest_name)})["tasks"]
    tasks = [(mongo.db.tasks.find_one({'_id': bson.ObjectId(i)})["task_name"], i) for i in tasks]
    return render_template('contest.html', admin=admin,
                           listOfTasks=tasks, contest_name=my_contest['name'], contest_id=contest_name,
                           username=session['username'], widgets=widgets
                           )


@app.route('/contest/<string:contest_name>/task/<string:task_name>')
@app.route('/task/<string:task_name>')
def task(contest_name=None, task_name=None):
    if 'username' not in session:
        return render_template('unauthorized.html')
    print(contest_name)

    task = mongo.db.tasks.find_one({"_id": bson.ObjectId(task_name)})

    if contest_name:
        my_contest = mongo.db.contests.find_one({"_id": bson.ObjectId(contest_name)})
        user = mongo.db.users.find_one({'username': session['username']})
        admin = user['admin']
        if error(user, admin, my_contest):
            return render_template("error.html")

    md = task["md"]["file_data"].decode()

    imagenames = re.findall(r"!\[.*?\]\(ai_.*?\)", md)
    for i in imagenames:
        name = i.split("(")[1][:-1]
        if name in task["res"]:
            f = open(f"/static/{name}", "wb")
            f.write(task["res"][name])
            f.close()

            md = md.replace(i, i.split("(")[0] + f"(/static/{name})")
        else:
            md = md.replace(i, i.split("(")[0] + f"(/static/placeholder)")

    md_template_string = markdown.markdown(
        md, extensions=["fenced_code", 'tables']
    ).replace("\n", "")

    if contest_name is not None:
        return render_template('task.html', url=task_name, username=session['username'],
                               contest_name=contest_name, statement=md_template_string)
    else:
        return render_template('task.html', url=task_name, username=session['username'],
                               statement=md_template_string)


def success_support_func(task_name):
    languages = {"Python 3.19": "python3", "C++ 17": "cpp", "Java": "java"}
    language = request.form['language']
    number = get_number(session["username"], task_name)
    f = request.files['file']
    return f.read(), number, languages[language]


@app.route('/task/<string:task_name>/success', methods=['POST'])
@app.route('/contest/<string:contest_id>/task/<string:task_name>/success', methods=['POST'])
def contest_success(contest_id=None, task_id=None):
    if request.method == 'POST':
        src, n, lang = success_support_func(task_id)
        if contest_id is not None:
            user = mongo.db.users.find_one({'username': session['username']})
            admin = user['admin']
            my_contest = mongo.db.contests.find_one({"_id": bson.ObjectId(contest_id)})
            if error(user, admin, my_contest):
                return render_template("error.html")
        _id = mongo.db.submissions.insert_one({'sender': session['username'],
                                               "datetime in UTC": datetime.now(timezone.utc),
                                               'task_name': task_id,
                                               'in_contest_name':
                                                   mongo.db.tasks.find_one({"_id": bson.ObjectId(task_id)})[
                                                       "task_name"],
                                               'source': src, 'n_try': n,
                                               'language': lang,
                                               'filename': request.files['file'].filename,
                                               'contest': 'No contest' if contest_id is None else contest_id,
                                               'verdict': "N/A",
                                               'final_verdict': "N/A"}).inserted_id
        if not isinstance(_id, str):
            _id = str(_id)
        q.lpush("job2", _id + ":3")
        return redirect('/submissions/1')


def get_string_submissions(submissions_arr):
    result = []
    for i in submissions_arr:
        result.append(f"time: {i['datetime in UTC']}; contest: {i['contest']}; task_name: {i['in_contest_name']};"
                      f" language: {i['language']}; verdict: {i['final_verdict']}")
    return result


@app.route('/submissions/<int:page_number>', methods=['POST', 'GET'])
def submissions(page_number):
    if 'username' not in session:
        return render_template('unauthorized.html')
    submissions_array = mongo.db.submissions.find({'sender': session['username']})
    submissions_array = sorted(submissions_array, key=lambda x: x['datetime in UTC'], reverse=True)
    limit_page = min(math.ceil(len(submissions_array) / 10), 1)
    submissions_array = submissions_array[(page_number - 1) * 10:page_number * 10]
    return render_template("submissions.html",
                           submissions_array=get_string_submissions(submissions_array), current_page=page_number,
                           limit_page=limit_page, username=session['username'])


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        signin_user = users.find_one({'username': request.form['username']})

        if signin_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), signin_user['password']):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        flash('Username and password combination is wrong')
        return render_template('signin.html')
    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


def check_vulnerabilities(file_str):
    tree = ast.parse(file_str)
    for i in ast.walk(tree):
        if isinstance(i, ast.ImportFrom) and i.module != 'cbacontest':
            raise ValueError('Use of modules other than cbacontest is forbidden')
        if isinstance(i, ast.Name) and i.id in ['eval', 'exec']:
            raise ValueError('Use of eval and exec is forbidden')
        if isinstance(i, ast.Name) and i.id in ['file', 'open']:
            raise ValueError('Use of files is forbidden')


@app.route('/create', methods=['GET', 'POST'])
def create_contest():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
    if request.method == 'POST':
        try:
            uploaded_file = request.files['type_python']
            filename = uploaded_file.filename
            file_data = uploaded_file.read()
            check_vulnerabilities(file_data)
            bson_document = {
                'filename': filename,
                'file_data': bson.Binary(file_data)
            }
            mongo.db.contests.insert_one({'name': request.form['ContestName'], 'tasks': [],
                                          'duration': min(request.form['duration'], '43800', key=lambda i: int(i)),
                                          'startTime': pytz.UTC.localize(datetime.strptime(request.form['StartTime'],
                                                                                           "%d/%m/%Y %H:%M:%S")),
                                          'allowed_teams': 'teams' in request.form,
                                          'description': request.form['description'],
                                          'config': bson_document,
                                          'global_events': [(0, "Start", {})],
                                          'groups': []})
            return redirect('contests/my')
        except ValueError as e:
            if 'int' in str(e):
                flash("Duration should be numerical")
            elif 'time' in str(e):
                flash("Write date in the format provided to you")
            else:
                flash(str(e))
            return redirect('/create')
    return render_template('create.html', admin=admin)


@app.route('/contest/<string:contest_id>/upload', methods=['GET', 'POST'])
def upload(contest_id):
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
    if request.method == 'POST':
        available_languages = [i if request.form[i] else None for i in ['py', 'java', 'cpp']]
        md = return_bson('md-file')[0]

        md_str = md["file_data"].decode()

        ai = re.findall(r"!\[.*?\]\(AI\)", md_str)
        c = 0
        jobs = []
        for i in ai:
            md_str = md_str.replace(i, i.split("(")[0] + f"(ai_{c})")
            jobs.append([i.split("]")[0][2:], c, "no"])
            c += 1

        md["file_data"] = md_str.encode()

        if 'input-file' in request.files and 'checker-file' in request.files and 'name' in request.form:
            input1 = return_bson('input-file')
            checker = return_bson('checker-file')
            _id = mongo.db.tasks.insert_one({"task_name": request.form['name'],
                                             "input": input1,
                                             "res": {},
                                             "checker": checker,
                                             "judgement_mod": request.form["judgement_mod"],
                                             "available": available_languages,
                                             "tags": request.form['tags'].split(","),
                                             'md': md}).inserted_id
        elif 'input-file' in request.files and 'solution-file' in request.files and 'name' in request.form:
            input1 = return_bson('input-file')
            solution = return_bson('solution-file')
            _id = mongo.db.tasks.insert_one({"task_name": request.form['name'],
                                             "input": input1,
                                             "res": [],
                                             "solution": solution,
                                             "judgement_mod": request.form["judgement_mod"],
                                             "available": available_languages,
                                             "tags": request.form['tags'].split(","),
                                             'md': md}).inserted_id
        elif 'input-file' in request.files and 'interactive-file' in request.files and 'name' in request.form:
            input1 = return_bson('input-file')
            interactive = return_bson('interactive-file')
            _id = mongo.db.tasks.insert_one({"task_name": request.form['name'],
                                             "input": input1,
                                             "res": [],
                                             "interactive": interactive,
                                             "judgement_mod": request.form["judgement_mod"],
                                             "available": available_languages,
                                             "tags": request.form['tags'].split(","),
                                             'md': md}).inserted_id
        elif 'input-file' in request.files and 'output-file' in request.files and 'name' in request.form:
            input1 = return_bson('input-file')
            output = return_bson('output-file')
            _id = mongo.db.tasks.insert_one({"task_name": request.form['name'],
                                             "input": input1,
                                             "res": [],
                                             "output": output,
                                             "judgement_mod": request.form["judgement_mod"],
                                             "available": available_languages,
                                             "tags": request.form['tags'].split(","),
                                             'md': md}).inserted_id

        for i in jobs:
            i[-1] = _id
            Thread(target=makeimage, args=i).run()

        if 'name' in request.form:
            mongo.db.contests.update_one({'_id': bson.ObjectId(contest_id)},
                                         {'$push': {'tasks': bson.ObjectId(_id)}})
        return redirect("contest/" + contest_id)
    return render_template('upload.html', admin=admin, contest_name=contest_id)


@app.route('/contest/<string:contest_id>/leaderboard/<int:page_number>', methods=['GET', 'POST'])
def leader_board(contest_id, page_number):
    board = []
    # leaders = {}
    for i in mongo.db.participants.find({'contest_id': contest_id}):
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
                           current_page=page_number, contest_name=contest_id)


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        groups = []
        for i in mongo.db.groups.find({}):
            if bson.ObjectId(mongo.db.users.find_one({'username': session['username']})['_id']) in i['members']:
                groups.append((i['_id'], i['name']))
        return render_template('personal.html', admin=admin, username=session['username'], groups=groups)


@app.route('/tasks_archive', methods=['GET', 'POST'])
def tasks_archive():
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        user = mongo.db.users.find_one({'username': session['username']})
        admin = user['admin']
        session['contests'] = []
        for i in mongo.db.contests.find():
            if not error(user, admin, i):
                session['contests'].append(str(i['_id']))
        contest_archive = [i for i in mongo.db.contests.find()
                           if i['_id'] not in session['contests'] and datetime.now(pytz.utc) >
                           i['startTime'].astimezone(pytz.utc)
                           + timedelta(minutes=int(i['duration']))]
        admin = mongo.db.users.find_one({'username': session['username']})['admin']
        archive = []
        for i in contest_archive:
            archive += [(mongo.db.contests.find_one(i['_id'])['name'],
                         j, mongo.db.tasks.find_one({'_id': j})['task_name']) for j in i['tasks']]
        print(archive)
        return render_template('tasks_archive.html', all_tasks=archive, admin=admin,
                               username=session['username'])


@app.route('/contests/<string:type_contests>', methods=['GET', 'POST'])
def available_contests(type_contests):
    if 'username' not in session:
        return render_template('unauthorized.html')
    else:
        user = mongo.db.users.find_one({'username': session['username']})
        admin = user['admin']
        if not admin and type_contests == 'my':
            return render_template('unauthorized.html')
        session['contests'] = []
        for i in mongo.db.contests.find():
            if not error(user, admin, i):
                session['contests'].append((i['name'], str(i['_id']), i['description']))
        if type_contests == 'available':
            return render_template('available.html', listOfUrls=session['contests'], admin=admin,
                                   username=session['username'])
        else:
            return render_template('my_contests.html', username=session['username'],
                                   listOfUrls=session['contests'], admin=admin)


@app.route('/manage_contest/<string:contest_id>', methods=['GET', 'POST'])
def manage_contest(contest_id):
    user = mongo.db.users.find_one({'username': session['username']})
    admin = user['admin']
    my_contest = mongo.db.contests.find_one({"_id": bson.ObjectId(contest_id)})
    if error(user, admin, my_contest):
        return render_template('error.html')
    if 'username' not in session:
        return render_template('unauthorized.html')
    tasks = mongo.db.contests.find_one({'_id': bson.ObjectId(contest_id)})["tasks"]
    tasks = [(mongo.db.tasks.find_one({'_id': bson.ObjectId(i)})["task_name"], i) for i in tasks]
    start_time = pytz.utc.localize(my_contest['startTime'])
    not_started, not_ended = False, False
    if start_time > datetime.now(pytz.utc):
        not_started = True
    elif datetime.now(pytz.utc) < start_time + timedelta(minutes=int(my_contest['duration'])) and not not_started:
        not_ended = True
    if request.method == 'POST':
        if 'group' in request.form:
            if request.form['group'] != '':
                group1 = mongo.db.groups.find_one({'_id': bson.ObjectId(request.form['group'])})
                mongo.db.contests.update_one({"_id": bson.ObjectId(contest_id)}, {'$push': {'groups': group1['_id']}})
            pass
        elif 'remove' in request.form:
            mongo.db.contests.update_one({"_id": bson.ObjectId(contest_id)},
                                         {"$pull": {"groups": bson.ObjectId(request.form["remove"])}})
        elif 'refresh' in request.form:
            id_ = bson.ObjectId(request.form["refresh"])
            md = mongo.db.tasks.find_one({"_id": id_})['md']
            md_str = md["file_data"].decode()
            refresh(md_str, id_)
        elif 'start' in request.form:
            mongo.db.contests.update_one({'_id': bson.ObjectId(contest_id)},
                                         {"$set": {'startTime': datetime.now(pytz.utc)}})
            return redirect('/contest/' + contest_id)
        elif 'end' in request.form:
            dif_time = (datetime.now(pytz.utc) -
                        pytz.utc.localize(my_contest['startTime']))
            mongo.db.contests.update_one({'_id': bson.ObjectId(contest_id)},
                                         {"$set": {'duration': dif_time.total_seconds() / 60}})
            return redirect('/contest/' + contest_id)
        else:
            for i in tasks:
                if request.form['id'] == str(i[1]):
                    mongo.db.tasks.delete_many({"_id": bson.ObjectId(i[1])})
                    mongo.db.contests.update_one({"_id": bson.ObjectId(contest_id)},
                                                 {"$pull": {"tasks": bson.ObjectId(i[1])}})
        return redirect('/manage_contest/' + contest_id)
    groups = [(i['name'], i['_id']) for i in mongo.db.groups.find({}) if i['_id'] not in my_contest['groups']]
    has_groups = len(groups) != 0
    groups_members = [(mongo.db.groups.find_one({"_id": i})["name"], i) for i in my_contest['groups']]
    return render_template('manage_contest.html', admin=admin,
                           listOfTasks=tasks, contest_name=my_contest['name'], contest_id=contest_id,
                           username=session['username'], not_started=not_started, not_ended=not_ended, groups=groups,
                           has_groups=has_groups, groups_members=groups_members)


@app.route('/group/<group_id>', methods=['GET', 'POST'])
def group(group_id):
    me = mongo.db.users.find_one({'username': session['username']})
    admin = me['admin']
    group_object = mongo.db.groups.find_one({"_id": bson.ObjectId(group_id)})

    members = [(mongo.db.users.find_one({"_id": bson.ObjectId(i)})['username'], i) for i in group_object['members']
               if me['_id'] != i]
    usernames = [(i['username'], i['_id']) for i in list(mongo.db.users.find({})) if (i['username'], i['_id'])
                 not in members and
                 me['_id'] != i['_id']]
    if 'username' not in session and not admin:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        if 'username' in request.form:
            person = request.form['username']
            mongo.db.groups.update_one({"_id": bson.ObjectId(group_id)}, {"$push": {"members": bson.ObjectId(person)}})
        elif 'delete_group' in request.form:
            identification = bson.ObjectId(group_id)
            mongo.db.groups.delete_one({"_id": bson.ObjectId(group_id)})
            for i in mongo.db.contests.find():
                if identification in i['groups']:
                    mongo.db.groups.update({}, {"$pull": {"groups": identification}})
            return redirect("/personal")
        else:
            for i in members:
                if str(request.form['delete']) == i[0]:
                    mongo.db.groups.update_one({"_id": bson.ObjectId(group_id)},
                                               {"$pull": {"members": bson.ObjectId(i[1])}})
                    break
        return redirect("/group/" + str(group_id))
    has_usernames = len(usernames) != 0
    return render_template('group.html', admin=admin, members=members,
                           group_name=group_object['name'], usernames=usernames, group_id=group_id,
                           has_usernames=has_usernames)


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    admin = mongo.db.users.find_one({'username': session['username']})['admin']
    if 'username' not in session and not admin:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        group1 = mongo.db.groups.find_one({'name': request.form['GroupName']})
        if group1 is not None:
            flash('Group with name ' + request.form['GroupName'] + ' already exists')
            return render_template('create_group.html', admin=admin)
        _id = mongo.db.groups.insert_one({'name': request.form['GroupName'],
                                          'members':
                                              [bson.ObjectId(mongo.db.users
                                                             .find_one({'username': session['username']})['_id'])],
                                          'description': request.form['description']}).inserted_id
        return redirect("/group/" + str(_id))
    return render_template('create_group.html', admin=admin)


if __name__ == "__main__":
    q = redis.StrictRedis(host=redis_host)
    app.run(host='0.0.0.0', debug=True)
