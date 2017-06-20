from urllib import urlencode
from httplib2 import Http
import json
import sys
import base64


print "Running Endpoint Tester....\n"
address = raw_input("Please enter the address of the server you want to access, \n If left blank the connection will be set to 'http://localhost:5000':   ")
if address == '':
	address = 'http://localhost:5000'

#TEST 1: TRY TO REGISTER A NEW USER
try:
	h = Http()
	url = address + '/api/v2/signup'
	data = dict(email="mandal@gmail.com", username="mandal", firstname="Vibhakar", lastname="mandal", password="Pan" )
	data = json.dumps(data)
	resp, content = h.request(url,'POST', body = data, headers = {"Content-Type": "application/json"})
	if resp['status'] != '201' and resp['status'] != '200':
 		raise Exception('Received an unsuccessful status code of %s' % resp['status'])

except Exception as err:
	print "Test 1 FAILED: Could not make a new user"
	print err.args
	sys.exit()
else:
	print "Test 1 PASS: Succesfully made a new user"

#TEST 2: OBTAIN A TOKEN
try:
	h = Http()
	h.add_credentials('mandal','Pan')
	url = address + '/api/v2/token'
	resp, content = h.request(url,'GET' , headers = {"Content-Type" : "application/json"})
	if resp['status'] != '200':
		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
	new_content = json.loads(content)
	if not new_content['token']:
		raise Exception('No Token Received!')
	token = new_content['token']
	print "received token: %s" % token
except Exception as err:
	print "Test 2 FAILED: Could not exchange user credentials for a token"
	print err.args
	sys.exit()
else:
	print "Test 2 PASS: Succesfully obtained token! "

#TEST 3: TRY TO ADD ISSUES TO DATABASE

try:
	h = Http()
	h.add_credentials(token,'blank')
	url = address + '/api/v2/user/createissue'
	data = dict(title="Import Error", description="Error while Importing Tensorflow and Pandas", user_assigned_to="mandal")
	resp, content = h.request(url,'POST', body = json.dumps(data), headers = {"Content-Type" : "application/json"})
	if resp['status'] != '200':
		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
	print "Test 3 FAILED: Could not add new issues"
	print err.args
	sys.exit()
else:
    print "Test 3 PASS: Succesfully added new issues"


#TEST 4: TRY ACCESSING ENDPOINT WITH AN INVALID TOKEN
try:
	h = Http()
	h.add_credentials("invalid-token",'blank')
	url = address + '/api/v2/resource'
	resp, content = h.request(url,'GET', headers = {"Content-Type" : "application/json"})
	if resp['status'] == '200':
		raise Exception("Security Flaw: able to log in with invalid credentials")
except Exception as err:
	print "Test 4 FAILED"
	print err.args
	sys.exit()
else:
    print "Test 4 PASS: App checks against invalid credentials"


#TEST 5: TRY TO VIEW ALL CREATED ISSUES IN DATABASE
try:
	h = Http()
	h.add_credentials(token,'blank')
	url = address + '/api/v2/user/issues/created'
	resp, content = h.request(url,'GET', headers = {"Content-Type" : "application/json"})
	if resp['status'] != '200':
		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
	print "Test 5 FAILED: Could not get issues"
	print err.args
	sys.exit()
else:
    print "All issues created by user"
    print content
    print "Test 5 PASS: Succesfully"

#TEST 6: TRY TO VIEW ALL ASSIGNED ISSUES IN DATABASE
try:
	h = Http()
	h.add_credentials(token,'blank')
	url = address + '/api/v2/user/issues/assigned'
	resp, content = h.request(url,'GET', headers = {"Content-Type" : "application/json"})
	if resp['status'] != '200':
		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
	print "Test 6 FAILED: Could not get issues"
	print err.args
	sys.exit()
else:
    print "All issues assigned to user:"
    print content
    print "Test 6 PASS: Succesfully"
