from django.conf import settings

import requests
from bs4 import BeautifulSoup
import json

class RepositoryManager(object):
	__name__ = 'RepositoryManager'

	def __init__(self, endpoint, **kwargs):
		self.endpoint = endpoint

		for k, v in kwargs.iteritems():
			setattr(self, k, v)

	def __repr__(self):
		return self.__name__

	def collections(self):
		return []

	def collection(self, collection_id):
		return []

	def get(self, uri):
		return {}

	def browse(self):
		return []

	def search(self, query):
		return []

class JARSManager(RepositoryManager):
	__name__ = 'JARS'

	getPattern = '{endpoint}/rest/resource/?uri={uri}'
	browsePattern = '{endpoint}/rest/resource/'
	collectionPattern = '{endpoint}/rest/collection/'
	collectionBrowsePattern = '{endpoint}/rest/collection/{collection}/'
	contentPattern = '{endpoint}{content_location}'
	token = settings.JARS_KEY

	def _cast(self, resource):
		return {
			'title': resource['name'],
			'uri': resource['uri'],
		}

	def _cast_collection(self, collection):
		return {
			'id': collection['id'],
			'title': collection['name'],
		}

	def collections(self):
		remote = self.collectionPattern.format(endpoint=self.endpoint)
		response = requests.get(remote, allow_redirects=True)
		jdata = json.loads(response.text)
		return [self._cast_collection(c) for c in jdata]

	def collection(self, collection_id):
		remote = self.collectionBrowsePattern.format(
			endpoint=self.endpoint,
			collection=collection_id
		)
		response = requests.get(remote, allow_redirects=True)
		jdata = json.loads(response.text)['resources']
		return [self._cast(r) for r in jdata if r['stored']]

	def browse(self):
		remote = self.browsePattern.format(endpoint=self.endpoint)
		response = requests.get(remote, allow_redirects=True)
		jdata = json.loads(response.text)

		return [self._cast(r) for r in jdata if r['stored']]

	def get(self, uri):
		remote = self.getPattern.format(endpoint=self.endpoint, uri=uri)
		headers = {
			'Authorization': 'Token {token}'.format(token=self.token),
		}
		response = requests.get(remote, allow_redirects=True)
		jdata = json.loads(response.text)[0]
		remoteContent = self.contentPattern.format(
			endpoint = self.endpoint,
			content_location = jdata['content_location']
		)
		responseContent = requests.get(remoteContent,
									   allow_redirects=True,
									   headers=headers)
		if responseContent.status_code != requests.codes.ok:
			raise RuntimeError('Error retrieving resource')

		textData = {
			'title': jdata['name'],
			'content': responseContent.text,
			'content-type': response.headers['content-type'],
		}
		return textData


class WebManager(RepositoryManager):
	__name__ = 'WWW'

	def get(self, uri):
		response = requests.get(uri, allow_redirects=True)
		soup = BeautifulSoup(response.text, "html.parser")

		textData = {
			'title': soup.title.string,
			'content': response.text,
			'content-type': response.headers['content-type'],
		}
		return textData

repositoryManagers = [
	('JARS', JARSManager),
	('WWW', WebManager),
]
