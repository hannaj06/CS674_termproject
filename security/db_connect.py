import psycopg2
import configparser
import datetime 


creds = configparser.ConfigParser()
creds.read('databases.conf')

class db_connect:

	def __init__(self, database):
		self.database = database
		dbname = creds.get(database, 'dbname')
		user = creds.get(database, 'user')
		password = creds.get(database, 'password')
		host = creds.get(database, 'host')
		port = creds.get(database, 'port')
		self.connection = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (dbname, user, password, host, port))
		self.cursor = self.connection.cursor()

	def query(self, query, var=''):
		if var=='':
			try:
				self.cursor.execute(query)
				self.connection.commit()	
			except Exception as e:
				raise e

		else:
			try:
				self.cursor.execute(query, var)
				self.connection.commit()
			except Exception as e:
				raise e

	def fetchall(self, query, var=''):
		#var = option for query string, must be TUPLE!
		if var=='':
			try:
				self.cursor.execute(query)
			except psycopg2.ProgrammingError as e:
				return {'results': 'error', 'ermessage': str(e)}
			except psycopg2.DataError as e:
				return {'results': 'error', 'ermessage': str(e)}
		else:
			try:
				self.cursor.execute(query, var)
			except psycopg2.ProgrammingError as e:
				return {'results': 'error', 'ermessage': str(e)}
			except psycopg2.DataError as e:
				return {'results': 'error', 'ermessage': str(e)}

		meta = self.cursor.description
		
		column_names = []

		if meta is not None:
			for names in meta:
				column_names.append(names[0])

		try:
			results = self.cursor.fetchall()
		except psycopg2.ProgrammingError as e:
			results = ['empty set']

		#if query results are empty
		if not results:
			a = [['empty', 'set'],['empty', 'set']]
			return {'results': ['empty set'], 'column_names' : column_names, 'html_table': '<h4>Empty Result Set!</h4>'}

		#return dictionatary of results, headers, and html table
		return {'results': results, 'column_names': column_names}








	def close(self):
		self.cursor.close()
		self.connection.close()