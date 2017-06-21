# Simple Issue Tracker API

a simple rest api for tracking issues.

## Python Libraries
The code in this repository assumes the following python libraries are installed:
* Flask
* SQLAlchemy
* httplib
* requests
* passlib
* itsdangerous
* flask-httpauth
* apscheduler

## Design:
System have two models called User and Issue. With following information:
### 1. User:
* Email
* Username
* FirstName
* LastName
* Password
* AccessToken

### 2. Issue:
* Title
* Description
* AssignedTo (User relation)
* Createdby (User relation)
* Status (Open, Closed)

## features
*  Every endpoint need user authentication.
* Authentication is stateless (access_token).
* User who created the issue is only be able to edit or delete that issue.
* Whenever an Issue is created or assigned to different user(in case of update), an email is triggered exactly after 12 mins to the particular user saying issue has been assigned to him/her.
* Every 24 hours an email is triggered to every users with details of all the issues assigned to him/her.

## Run
#### Start server
    $ python main.py
#### Test client
    $ python test.py
