from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

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
		#temp_and_hum = temp_and_hum.split(',')

		return temp_and_hum

	raise Exception('Error: couldn\'t get content from response')

if __name__ == '__main__':
	url = 'http://thermo.local/weather'

	data = search_resp_for_weather(get_req(url))

	print(data)

