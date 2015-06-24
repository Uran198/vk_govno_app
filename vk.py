import requests
import json
import urllib.request
from urllib.request import pathname2url
import logging

oauth_link = "https://oauth.vk.com/authorize?client_id=4967910&redirect_uri=https://oauth.vk.com/blank.html&scope=12&display=mobile&response_type=token"
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
		req_url = self.__api_url+'/'+pathname2url(method)
		params = params.copy()
		params['access_token'] = self.__access_token
		return requests.get(req_url, params=params)

	def oauth(self):
		return

if __name__ == '__main__':
	vk = VK(uid="171937039")
	#need set start_time and track it not to process the same posts
	params = {"q" : "#розыгрыш", "extended" : "1", "count" : "1"}
	resp = vk.call_method("newsfeed.search", params)
	print(resp.text)
