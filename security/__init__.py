import tornado.httpserver
import tornado.ioloop
import tornado.web
import os
import json
import requests
import hashlib
from slacker import Slacker
from jinja2 import Environment, FileSystemLoader
from security.db_connect import db_connect

templateLoader = FileSystemLoader( searchpath = "templates/" )
templateEnv = Environment( loader = templateLoader , cache_size=0)
login_page = templateEnv.get_template("login.html")
main_page = templateEnv.get_template("main.html")
sorry_page = templateEnv.get_template("sorry.html")

# db = db_connect('postgres')
# cookie_secret = db.fetchall("SELECT * FROM cookie_secret;")
# cookie_secret = cookie_secret['results'][0][0]
# db.close()
cookie_secret='test'
class BaseHandler(tornado.web.RequestHandler):
	def auth_check(self):
		cookie = self.get_secure_cookie('CS674_user')

		if not cookie:
			self.redirect('/login')
		else:
			user_cookie = json.loads(cookie)
			db = db_connect('webapp_noauth')
			auth = db.fetchall("""SELECT * FROM user_auth(%s, %s)""", (user_cookie['user_name'], user_cookie['pass']))
			db.close()

			if auth['results'][0][0]:
				return True
			else:
				self.redirect('/login')