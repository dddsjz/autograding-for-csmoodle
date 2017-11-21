_author_ = 'dddsjz'

# Reference: http://cuiqingcai.com/1052.html

# coding=utf-8

import ssl
import urllib
import urllib2
import cookielib
import json
import re

# 2017.11.1: logic should like this use re to get sesskey, student_id, and student_name(with a white space) and store id
# and name into a local file. User should input student_name and program will find the student_id and construct request.

# 2017.11.2: create a regular express to find the 5 digit student id which is used to recognize student in server.
# the logic for regular express is: The 5 digit number will following "id=", so 'id=(\d{5})'. And following this part will
# be some characters but never include an url which has "://" (a simple way to search the result), so '.[^://*]'

# Login input
login_name = raw_input("Please Enter login name\n")
password = raw_input("Please Enter Password\n")

# close verified certificate
ssl._create_default_https_context = ssl._create_unverified_context

# install proxy
enable_proxy = False
# https
proxy_handler = urllib2.ProxyHandler({"https": '127.0.0.1:8080'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib2.build_opener(proxy_handler)
else:
    opener = urllib2.build_opener(null_proxy_handler)
urllib2.install_opener(opener)
# debug proxy
#response = urllib2.urlopen('https://www.baidu.com')
#print response.read()

# store a login cookie for current session
filename = 'cookie.txt'
cookie = cookielib.MozillaCookieJar(filename)
# login header
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
content_type = "application/x-www-form-urlencoded"
referer = "https://csmoodle.ucd.ie/moodle/login/index.php"
headers = {"User-Agent":user_agent, "Content-Type":content_type, "Referer":referer}
# value for post login form
value = {"username":login_name, "password":password, "rememberusername":1}
data = urllib.urlencode(value)
url = "https://csmoodle.ucd.ie/moodle/login/index.php"
req = urllib2.Request(url, data, headers)
if enable_proxy:
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), proxy_handler)
else:
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), null_proxy_handler)
response = opener.open(req)
#print response.read()

sesskey = re.findall(r'sesskey=(\w*?)\"', response.read())[0]
# print sesskey
# save & rewrite old file
cookie.save(ignore_discard=True, ignore_expires=True)

# ask / to find courses by courses ID

# ask view.php to get inside to courses and find subject id

# ask grading web page and find student id
student_name = raw_input("Please Enter Student Name:\n")
grade = raw_input("Please Enter Grade:\n")
while(student_name!="Exit"):
    url = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id=41885&action=grading"
    referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id=41885"
    headers = {"User-Agent":user_agent, "Referer":referer}
    req = urllib2.Request(url, headers=headers)
    response = opener.open(req)
    # print response.read()
    student_id = re.findall(r'id=(\d{5})(.[^://]*)'+student_name, response.read())[0][0]
    # print student_id
    # print response.read()

    # find assignmentid from user-info data region.

    # json header
    gradeUrl = "https://csmoodle.ucd.ie/moodle/lib/ajax/service.php?sesskey="+sesskey+"&info=mod_assign_submit_grading_form"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
    content_type = "application/json"
    accept_encoding = "gzip,deflate,br"
    host = "csmoodle.ucd.ie"
    referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id=41885&rownum=0&action=grader&userid=12840"
    x_requested_with = "XMLHttpRequest"
    headers = {"Host":host, "User-Agent":user_agent, "Accept-Encoding":accept_encoding, "Content-Type":content_type, "Referer":referer, "X-Requested-With": x_requested_with}
    # json value
    value = [{
        "index":0,
        "methodname":"mod_assign_submit_grading_form",
        "args":{
            "assignmentid":"4195",
            "userid":student_id,
            "jsonformdata":"\"id=41885"
                        "&rownum=0"
                        "&useridlistid="
                        "&attemptnumber=-1"
                        "&ajax=0"
                        "&userid="+student_id+""
                        "&sendstudentnotifications=false"
                        "&action=submitgrade"
                        "&sesskey="+sesskey+""
                        "&_qf__mod_assign_grade_form_"+student_id+"=1"
                        "&grade="+grade+""
                        "&assignfeedbackcomments_editor%5Btext%5D="
                        "&assignfeedbackcomments_editor%5Bformat%5D=1"
                        "&addattempt=0\""}}]
    data = json.dumps(value)
    # print data
    gradereq = urllib2.Request(gradeUrl, data, headers)
    result = opener.open(gradereq)
    student_name = raw_input("Please Enter Student Name:\n")
    grade = raw_input("Please Enter Grade:\n")

print result.read()