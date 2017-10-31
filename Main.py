_author_ = 'dddsjz'

# Reference: http://cuiqingcai.com/1052.html

# coding=utf-8

import ssl
import urllib
import urllib2
import cookielib
import json
import re

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
headers = {"User-Agent":user_agent,"Content-Type":content_type,"Referer":referer}
# value for post login form
value = {"username":"","password":"","rememberusername":1}
data = urllib.urlencode(value)
url = "https://csmoodle.ucd.ie/moodle/login/index.php"
req = urllib2.Request(url, data, headers)

if enable_proxy:
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), proxy_handler)
else:
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), null_proxy_handler)

response = opener.open(req)

sesskey = re.findall(r'sesskey=(.+?)\"', response.read())[1]

#print sesskey
#print response.read()
# save & rewrite old file
cookie.save(ignore_discard=True, ignore_expires=True)

# json header
gradeUrl = "https://csmoodle.ucd.ie/moodle/lib/ajax/service.php?sesskey="+sesskey+"&info=mod_assign_submit_grading_form"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
content_type = "application/json"
accept_encoding = "gzip,deflate,br"
host = "csmoodle.ucd.ie"
referer = "https://csmoodle.ucd.ie/moodle/mod/assign/view.php?id=41883&rownum=0&action=grader&userid=12840"
x_requested_with = "XMLHttpRequest"
headers = {"Host":host, "User-Agent":user_agent, "Accept-Encoding":accept_encoding, "Content-Type":content_type, "Referer":referer, "X-Requested-With": x_requested_with}
# json value
value = [{"index":0, "methodname":"mod_assign_submit_grading_form","args":{"assignmentid":"4194","userid":12840,"jsonformdata":"\"id=41883&rownum=0&useridlistid=&attemptnumber=-1&ajax=0&userid=12840&sendstudentnotifications=true&action=submitgrade&sesskey="+sesskey+"&_qf__mod_assign_grade_form_12840=1&grade=20.00&assignfeedbackcomments_editor%5Btext%5D=&assignfeedbackcomments_editor%5Bformat%5D=1&addattempt=0\""}}]
data = json.dumps(value)
#print data
gradereq = urllib2.Request(gradeUrl, data, headers)
result = opener.open(gradereq)

print result.read()