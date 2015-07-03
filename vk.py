#
#
# config.json structure:
#	{
#		"uid": {
#			"access_token":"your_token"
#		}
#	}
# access_token you can get by following oaut_link below
#
#
import requests
import json
import logging
from time import sleep
from operator import itemgetter
import os

oauth_link = "https://oauth.vk.com/authorize?client_id=4967910&redirect_uri=https://oauth.vk.com/blank.html&scope={scope}&display=mobile&response_type=token".format(scope='messages ')

logger = logging.getLogger('warning')
logger.setLevel(logging.WARNING)

class VK:
	__api_url = "https://api.vk.com/method/"
	#in config file you have ids & access tokens
	__config_file = 'config.json'
	__config_data = None

	def __init__(self, uid=None):
		if not self.__config_data:
			self.__config_data = json.load(open(self.__config_file))
		if uid and self.__config_data.get(uid, None):
			self.__access_token = self.__config_data[uid]['access_token']
		else:
			if not self.__config_data.get(uid, None):
				logger.warning("Couldn't find uid '{0}' in config file '{1}'".format(uid, self.__config_file))
				logger.warning("You should add access_token to config file to use this uid")
				logger.warning("You can do it by following the link:")
				logger.warning(oath_link)
			self.__access_token = ''

	def call_method(self, method, params):
		req_url = self.__api_url+'/'+method
		params = params.copy()
		params['access_token'] = self.__access_token
		return requests.get(req_url, params=params)

class Notifier:
	def __init__(self,uid):
		self.vk = VK(uid)

	def _get_data(self,resp):
		resp.raise_for_status()
		data = json.loads(resp.text)
		if not data.get('response', None):
			print(data)
			exit(1)
		return data['response']

	def _get_icon(self, uid):
		params =\
				{
						'user_ids' : str(uid),
						'fields' : 'photo_50',
				}
		resp = self.vk.call_method('users.get', params)
		data = self._get_data(resp)
		icon_url = data[0]['photo_50']
		resp = requests.get(icon_url, stream=True)
		resp.raise_for_status()
		icon_loc = 'icon.png'
		with open(icon_loc, 'wb') as f:
			for chunk in resp:
				f.write(chunk)
		return icon_loc, data[0]['first_name'], data[0]['last_name']

	def _sanitized(self, text):
		return text.replace("'", "\"").replace("\\", "\\\\")

	def send_notify(self, uid, title, body):
		icon,name,surname = self._get_icon(uid)
		summary = title + ", "  + name + ' ' + surname
		# May be danherous to call os.system
		summary = self._sanitized(summary)
		body = self._sanitized(body)
		os.system("notify-send -i $(pwd)/{icon} '{summary}' '{body}'".format(
			icon = icon, summary = summary, body = body))

	def run(self):
		params =\
			{
			'out': '0',
			'count' : '1',
			'time_offset' : '0',
			'preview_length' : '0',
			}
		resp = self.vk.call_method("messages.get", params)
		#raise exeption if not 200
		data = self._get_data(resp)
		data = sorted(data[1:], key=itemgetter('date'))
		last_message_id = data[0]['mid']
		params['count'] = '200'
		while True:
			params['last_message_id'] = last_message_id
			resp = self.vk.call_method("messages.get", params)
			data = self._get_data(resp)
			data = sorted(data[1:], key=itemgetter('date'))
			for row in data:
				print(row)
				uid = row['uid']
				title = row['title']
				body = row['body']
				self.send_notify(uid, title, body)
				last_message_id = max(row['mid'],last_message_id)
			sleep(1)


if __name__ == '__main__':
	notifier = Notifier(uid="171937039")
	notifier.run()
