# -*- coding: UTF-8 -*-
# !/usr/bin/env python

_author_ = 'dddsjz'

import ssl
import urllib
import urllib2
import cookielib
import json
import re
from Tkinter import *
import os

# Reference: http://cuiqingcai.com/1052.html

# 2017.11.1: logic should like this use re to get sesskey, student_id, and student_name(with a white space) and store id
# and name into a local file. User should input student_name and program will find the student_id and construct request.

# 2017.11.2: create a regular express to find the 5 digit student id which is used to recognize student in server.
# the logic for regular express is: The 5 digit number will following "id=", so 'id=(\d{5})'. And following this part will
# be some characters but never include an url which has "://" (a simple way to search the result), so '.[^://*]'

# 2017.11.27: finished all basic function, want to add GUI and download file function

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

# Tkinter initialization
# top = Tk()
# top.title = ("Grade")
# top.geometry('200X200')
# top.resizable(width=True,height=True)

# Three frames, top with login, left with courses and subjects, right with student and grade
# frm_tp = Frame(top)

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"

# store a login cookie for current session
filename = 'cookie.txt'
cookie = cookielib.MozillaCookieJar(filename)


def login(login_name, password, course_in):
    global opener
    # login header
    content_type = "application/x-www-form-urlencoded"
    referer = "https://csmoodle.ucd.ie/moodle/login/index.php/"
    headers = {"User-Agent":user_agent, "Content-Type":content_type, "Referer":referer}
    # value for post login form
    value = {"username":login_name, "password":password, "rememberusername":1}
    data = urllib.urlencode(value)
    url = "https://csmoodle.ucd.ie/moodle/login/index.php/"
    req = urllib2.Request(url, data, headers)
    if enable_proxy:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), proxy_handler)
    else:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), null_proxy_handler)
    response = opener.open(req)
    rr = response.read()
    # print rr

    sesskey = re.findall(r'sesskey=(\w*?)\"', rr)[0]
    user_id = re.findall(r'userid=\"(\d{5,})\"', rr)[0]
    print user_id
    # print sesskey
    # save & rewrite old file
    cookie.save(ignore_discard=True, ignore_expires=True)

    # ask / to find courses by courses ID

    course_id = re.findall(r'id=(\d{3,}).*' + course_in, rr)
    print course_id
    return sesskey, user_id, course_id


# Login input
login_name = raw_input("Please Enter login name\n")
password = raw_input("Please Enter Password\n")
course_in = raw_input("Please Enter Course ID\n")
temp = login(login_name, password, course_in)

sesskey = temp[0]
user_id = temp[1]
course_id = temp[2]

# ask view.php to get inside to courses and find subject id
url = "https://csmoodle.ucd.ie/moodle/course/view.php?id="+course_id[0]+"/"
referer = "https://csmoodle.ucd.ie/moodle/"
headers = {"User-Agent":user_agent, "Referer":referer}
req = urllib2.Request(url, headers=headers)
response = opener.open(req)
rr = response.read()
print rr

# find instance name to choose the subject to grade
subjects = re.findall(r'id=(\d{5,}).*?instancename">(.*?)<', rr)
print subjects

# find subject id
subject_name = raw_input("Please Choose A Subject\n")
subject_index = -1
for i in subjects:
    for j in i:
        if subject_name == j:
            subject_index = i[0]

print subject_index

# find assignmentid from user-info data region.
url = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id="+subject_index+"&rownum=0&action=grader/"
referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id="+subject_index+"/"
headers = {"User-Agent": user_agent, "Referer": referer}
req = urllib2.Request(url, headers=headers)
response = opener.open(req)
assignment_id = re.findall(r'data-assignmentid=\"(\d{4,})\"',response.read())[0]
print assignment_id


def grade_student(student_name, grade):
    while(student_name!="Exit"):
        url = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id="+subject_index+"&action=grading/"
        referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id="+subject_index
        headers = {"User-Agent":user_agent, "Referer":referer}
        req = urllib2.Request(url, headers=headers)
        response = opener.open(req)
        rr = response.read()
        # print response.read()
        student_id = re.findall(r'id=(\d{5})(.[^://]*)'+student_name, rr)[0][0]
        temp = re.findall(r'user'+student_id+'.*?([\s\S]*?)pluginfile.php(.*?)c9',rr)
        #print temp
        #print "temp 0 0 : "+temp[0][0] + "\n"
        #print "temp 0 1 : "+temp[0][1] + "\n"
        # print temp[1]
        combine = temp[0][0] + 'pluginfile.php' + temp[0][1]
        check = re.findall('cell c8[\s\S]*?</tr>', combine)
        # print check
        # print combine
        print student_id
        # print response.read()
        if check.__len__() == 0:
            download_url = re.findall(r'[a-zA-z]+://[^\s]*', re.findall(r'<a target.*?="(.*?)">', combine)[0])
            # print download_url
            #local.replace('\\','\/')

            #local = r'C:\temp'+'\\'+student_name+r'\1.zip'
            #print local
            # local = re.sub(r'\\', '/', local)
            # print local
            local = '''D:\temp\1'''
            urllib.urlretrieve(download_url[0], local)
        else:
            print("No any file to download")

        # json header
        # gradeUrl = "https://csmoodle.ucd.ie/moodle/lib/ajax/service.php?sesskey="+sesskey+"&info=mod_assign_submit_grading_form/"
        content_type = "application/json"
        accept_encoding = "gzip,deflate,br"
        host = "csmoodle.ucd.ie"
        # referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id="+subject_index+"&rownum=0&action=grader&userid="+user_id
        x_requested_with = "XMLHttpRequest"
        headers = {"Host":host, "User-Agent":user_agent, "Accept-Encoding":accept_encoding, "Content-Type":content_type, "Referer":referer, "X-Requested-With": x_requested_with}
        # json value
        value = [{
            "index":0,
            "methodname":"mod_assign_submit_grading_form",
            "args":{
                "assignmentid":assignment_id,
                "userid":student_id,
                "jsonformdata":"\"id="+subject_index+""
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
        # data = json.dumps(value)
        # print data
        # gradereq = urllib2.Request(gradeUrl, data, headers)
        # result = opener.open(gradereq)
        # print result.read()
        student_name = raw_input("Please Enter Student Name:\n")
        grade = raw_input("Please Enter Grade:\n")


    return 0



# ask grading web page and find student id
student_name = raw_input("Please Enter Student Name:\n")
grade = raw_input("Please Enter Grade:\n")
grade_student(student_name, grade)
