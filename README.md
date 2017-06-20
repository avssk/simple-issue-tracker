# Simple Issue Tracker API

a simple api for tracking issues.

## Python Libraries
The code in this repository assumes the following python libraries are installed:
* Flask
* SQLAlchemy
* httplib
* requests
* oauth2client
* redis
* passlib
* itsdangerous
* flask-httpauth

## Design:
System have two models called User and Issue. With following information
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
*  Every endpoint need user authentication
* Authentication should be stateless (access_token)
* User who created the issue only should be able to edit or delete that issue

## Run
#### Start server
    $ python main.py
#### Test client
    $ python test.py
