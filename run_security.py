from security import *
from security.db_connect import db_connect

single_process = True

class main(BaseHandler):
	def get(self):
		if self.auth_check()==True:
			user_info = json.loads(self.get_secure_cookie('CS674_user'))
			db = db_connect('webapp_auth')
			class_schedule = db.fetchall("""select class_name from courses
							join classes on classes.class_id = courses.class_id
							join security_services on security_services.user_id = courses.student_id
							where user_name = %s
							order by class_name;""", (user_info['user_name'], ) 
							)
			

			study_buddies = db.fetchall("""select user_name, class_name, dorm from courses
											join classes on classes.class_id = courses.class_id
											join security_services on security_services.user_id = courses.student_id
											join dorm on dorm.student_id = courses.student_id
											where courses.class_id in (select class_id from courses where student_id = %s) and courses.student_id != %s
											order by class_name;""", (user_info['user_id'], user_info['user_id']))

			db.close()
		 	html_output = main_page.render(study_buddies = study_buddies, class_schedule=class_schedule, user_info=user_info)
			self.write(html_output)


class logout(BaseHandler):
	def get(self):
		self.clear_cookie('CS674_user')
		self.redirect("/login")


class login(BaseHandler):
	def get(self):
		html_output = login_page.render() 
		self.write(html_output)
	
	def post(self):
		user_name = self.get_argument('user_name', '')
		password = hashlib.md5(self.get_argument('password', ''))
		db = db_connect('webapp_noauth')
		auth = db.fetchall("""SELECT * FROM user_auth(%s, %s)""", (user_name, password.hexdigest()))
		db.close()

		if auth['results'][0][0]:
			self.clear_cookie('CS674_user')
			self.set_secure_cookie('CS674_user', json.dumps({'user_id': auth['results'][0][0], 'user_name': auth['results'][0][3], 'pass': auth['results'][0][2], 'account_type': auth['results'][0][9]}),expires_days=1)
		 	self.redirect('/')
		elif not auth['results'][0][0]:
			html_output = login_page.render(message = 'Invalid user_name or password!') 
			self.write(html_output)



def make_app():
	settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}
	return tornado.web.Application([
		(r"/", main),
		(r"/login", login),
		(r"/logout", logout),
		], debug=single_process, cookie_secret=cookie_secret, **settings)

if __name__ == "__main__":
	if single_process==False: 
		app = make_app()
		server=tornado.httpserver.HTTPServer(app) 
		server.bind(8020)
		server.start(0)
		try: 
			tornado.ioloop.IOLoop.current().start()
		except KeyboardInterrupt: 
			tornado.ioloop.IOLoop.instance().stop() 

	else: 
		app = make_app()
		app.listen(8020)
		tornado.ioloop.IOLoop.current().start()