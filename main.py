from models import Base, User, Issue
from flask import Flask, jsonify, request, url_for, abort, g, render_template, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import random, string
import requests, logging, os, time
from apscheduler.schedulers.background import BackgroundScheduler


from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


engine = create_engine('sqlite:///SIT.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route("/api/v2/token")
@auth.login_required
def generate_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token':token.decode('ascii')})


@app.route('/api/v2/user/logout', methods = ['GET'])
@auth.login_required
def logout():
    g.user = None
    return jsonify({"result": True})


@app.route('/api/v2/user/login', methods = ['POST'])
def api_login():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        print "missing arguments"
        abort(400)
    username = request.json.get('username')
    password = request.json.get('password')
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return jsonify({"result": False})
    token = user.generate_auth_token(6000)
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/v2/signup', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400)

    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200
    email = request.json.get('email')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    user = User(email = email, username = username, firstname = firstname, lastname = lastname)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201

# for testing purpose
@app.route('/api/v2/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })


@app.route('/api/v2/user/createissue', methods = ['POST'])
@auth.login_required
def createIssues():
    title = request.json.get('title')
    description = request.json.get('description')
    user_assigned_to = request.json.get('user_assigned_to')
    user_assigned_to_id = getID(user_assigned_to)
    user = g.user
    user_assigned_by_id = user.id
    status = 'open'
    newIssue = Issue(title=title, description=description, user_assigned_to_id=user_assigned_to_id, user_assigned_by_id=user_assigned_by_id, status = status)
    session.add(newIssue)
    session.commit()
    return jsonify(newIssue.serialize)


# list all issues of that user
@app.route('/api/v2/user/issues/created')
@auth.login_required
def allCreatesdIssues():
    user = g.user
    user_id = user.id
    issues = session.query(Issue).filter_by(user_assigned_by_id = user_id).all()
    return jsonify(issues = [issue.serialize for issue in issues])


# list all issues assigned to that user
@app.route('/api/v2/user/issues/assigned')
@auth.login_required
def allAssignedIssues():
    user = g.user
    user_id = user.id
    issues = session.query(Issue).filter_by(user_assigned_to_id = user_id).all()
    return jsonify(issues = [issue.serialize for issue in issues])


# show, edit or delete a specific issue
@app.route('/api/v2/user/issues/<id>', methods = ['GET','PUT', 'DELETE'])
def issue_handler(id):
    issue = session.query(Issue).filter_by(id = id).one()
    # Show a specific issue
    if request.method == 'GET':
        return jsonify(issue = issue.serialize)
        # modify a specific issue
    elif request.method == 'PUT':
        title = request.json.get('title')
        description = request.json.get('description')
        user_assigned_to = request.json.get('user_assigned_to')
        user_assigned_to_id = getID(user_assigned_to)
        status = request.json.get('status')
        if title:
            issue.title = title
        if description:
            issue.description = description
        if user_assigned_to_id:
            issue.user_assigned_to_id = user_assigned_to_id
        if status:
            issue.status = status
        session.commit()
        time.sleep(12*60)
        user = session.query(User).filter_by(id = user_assigned_to_id).first()
        email = user.email
        firstname = user.firstname
        lastname = user.lastname
        send__mail(firstname, lastname, email, title, description, id)
        return jsonify(issue = issue.serialize)
        # delete a specific issue
    elif request.method == 'DELETE':
  	session.delete(issue)
  	session.commit()
  	return "Issue Deleted"


def getID(username):
    user = session.query(User).filter_by(username = username).first()
    if not user:
        print "User does not exists"
        abort(400)
    else:
        return user.id

def send__mail(firstname, lastname, email, title, description, issue_id):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox7247fe0615ed4ff9a3980ab9b516f864.mailgun.org/messages",
        auth=("api", "MAILGUN-API-KEY"),
        data={"from": "Simple Issue Tracker <priyanshudeveloper@gmail.com>",
              "to": firstname+" "+lastname+" <"+email+"> ",
              "subject": "Issue: #id:" + issue_id + " :" + title,
              "text": "This isssue is assigned to you" + "\n" + "Issue Description: "+description})

def send__alert():
    issues = session.query(Issue).all()
    issues = jsonify(issues = [issue.serialize for issue in issues])
    for i in range(len(issues)):
        issue_id = issues[i]['id']
        title = issues[i]['title']
        description = issues[i]['description']
        user = session.query(User).filter_by(id = issues[i]['user_assigned_to_id']).first()
        email = user.email
        firstname = user.firstname
        lastname = user.lastname
        send__mail(firstname, lastname, email, title, description, issue_id)

scheduler = BackgroundScheduler()
scheduler.add_job(send__alert, 'interval', hours=24)
scheduler.start()

if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)
