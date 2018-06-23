from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime, date, time
import sqlite3
import enum

def get_req(url):
	try:
		with closing(get(url, stream=True)) as resp:
			if good_resp(resp):
				return resp.content

			else:
				return None

	except RequestException as e:
		print('Error during request to {0} : {1}'.format(url, str(e)))
		return None

def good_resp(resp):

	content_type = resp.headers['Content-Type'].lower()

	return (resp.status_code == 200 
			and content_type is not None 
			and content_type.find('html') > -1)


def search_resp_for_weather(resp):

	if resp is not None:
		html = BeautifulSoup(resp, 'html.parser')
		temp_and_hum = html.p.string.replace(' ', '').split(',')
		temp_and_hum[0] = int(temp_and_hum[0])
		temp_and_hum[1] = int(temp_and_hum[1])

		return temp_and_hum

	raise Exception('Error: couldn\'t get content from response')

def insert_new_weather_data(context):
	inserted = False
	conn = sqlite3.connect(context['month'] + '.db')
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
			c.execute('INSERT INTO {0} VALUES (?,?,?,?)'.format('Day' + context['day']),
																(context['hour'],
																context['minute'],
																context['temp'],
																context['humid']))
			conn.commit()

		except sqlite3.OperationalError as e:
			print(e)

		
	finally:
		print('database updated')
		conn.close()

def create_weather_context(t_and_h):
	ts = datetime.now()
	context = {
		'temp' : t_and_h[0],
		'humid' : t_and_h[1],
		'month' : datetime.now().strftime('%B'),
		'day' : datetime.now().strftime('%d'),
		'hour' : int(datetime.now().strftime('%H')),
		'minute' : int(datetime.now().strftime('%M'))
	}

	return context

if __name__ == '__main__':
	
	url = 'http://thermo.local/weather'
	t_and_h = search_resp_for_weather(get_req(url))
	#ts = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
	context = create_weather_context(t_and_h)
	print(context)

	insert_new_weather_data(context)

