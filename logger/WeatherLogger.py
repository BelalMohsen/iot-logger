from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime, date, time
import sqlite3
import json

class WeatherLogger:

	def __init__(self, url_of_sensor, path_to_db):
		self.url = url_of_sensor
		self.root_dir = path_to_db

	def request_weather(self):
		try:
		with closing(get(self.url, stream=True)) as response:
			if check_response(response):
				return response.content

			else:
				return None

		except RequestException as e:
			print('Error during request to {0} : {1}'.format(url, str(e)))
			return None

	def check_response(response):
		content_type = response.headers['Content-Type'].lower()

		return (response.status_code == 200 
				and content_type is not None 
				and content_type.find('html') > -1)

	def get_data_from_response(response):
		if response is not None:
			html = BeautifulSoup(response, 'html.parser')
			data = html.p.string
			data_dict = json.load(data)

			return data_dict

		else:
			raise Exception('Error: response contained not data')

	def update_weather_record(self, context):
		conn = sqlite3.connect(self.root_dir + '/' + context['month'] + '.db')
		c = conn.cursor()
		
		try:
			c.execute('INSERT INTO {0} VALUES (?,?,?,?)'.format('Day' + context['day']),
																(context['hour'],
																context['minute'],
																context['temp'],
																context['humid']))
			conn.commit()

		except sqlite3.OperationalError as e:
			print(e)
			print('Attempting to create and reinsert')
			
			try:
				c.execute('CREATE TABLE {} (Hour text PRIMARY KEY, Minute text, Temp int, Humid int)'.format('Day' + context['day']))
				print('table created')
				c.execute('INSERT INTO {0} VALUES (?,?,?,?)'.format('Day' + context['day']),
																	(context['hour'],
																	context['minute'],
																	context['temp'],
																	context['humid']))
				print('data inserted')
				conn.commit()

			except sqlite3.OperationalError as e:
				print(e)

			
		finally:
			print('database updated, now closing')
			conn.close()

	def create_weather_context(weather_data):
		ts = datetime.now()
		context = {
			'temp' : weather_data['temp'],
			'humid' : weather_data['humid'],
			'month' : datetime.now().strftime('%B'),
			'day' : datetime.now().strftime('%d'),
			'hour' : int(datetime.now().strftime('%H')),
			'minute' : int(datetime.now().strftime('%M'))
		}

		return context




