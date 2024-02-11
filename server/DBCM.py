import psycopg2
#from logger import logger
from flask import Blueprint, render_template


class UseDatabase:

	def __init__(self, config: dict):
		self.configuration = config

	def __enter__(self):
		# try:
		self.conn = psycopg2.connect(**self.configuration)
		self.cursor = self.conn.cursor()
		return self.cursor

		# except Exception as e:
		# 	logger.error(e)
		# 	raise DBConnectionError

	def __exit__(self, exception_type, exception_value, traceback):
		# try:
		self.conn.commit()
		self.cursor.close()
		self.conn.close()

		# except Exception as err:
		# 	logger.error(err)
		# 	return render_template('db_error.html')


class DBConnectionError(Exception):
	pass


class DBClosingError(Exception):
	pass


error_blueprint = Blueprint('error_blueprint', __name__, template_folder='templates')


@error_blueprint.route('/', methods=['GET', 'POST'])
def render_error():
	return render_template('db_error.html')