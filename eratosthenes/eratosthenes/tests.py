import unittest
from django.contrib.auth.models import User
from models import Repository, Text
from provider.oauth2.models import Client
from managers import WebManager, JARSManager
from tasks import get

wikiURL = 'https://en.wikipedia.org/wiki/Eratosthenes'
jars_uri = 'http://jars/localresource/6'

class TestJARSManager(unittest.TestCase):
	def setUp(self):
		self.manager = JARSManager(
			'http://localhost:8002',
			token='050814a54ac5c81b990140c3c43278031d391676',
		)

	def test_get(self):
		textData = self.manager.get("http://jars/localresource/6")
		self.assertIsInstance(textData, dict)
		self.assertIn('content', textData)
		self.assertIn('content-type', textData)
		self.assertIn('title', textData)


class TestWWWManager(unittest.TestCase):
	def setUp(self):
		self.manager = WebManager('')

	def test_get(self):
		textData = self.manager.get(wikiURL)
		self.assertIsInstance(textData, dict)
		self.assertIn('content', textData)
		self.assertIn('content-type', textData)
		self.assertIn('title', textData)


class TestGetWWW(unittest.TestCase):
	def setUp(self):
		self.repository = Repository(
			name='TestRepository',
			manager='WWW',
			endpoint='',
		)
		self.repository.save()

		self.user = User(
			username = 'Bob',
			password = 'bobpass',
		)
		self.user.save()

		self.client = Client(
			user=self.user,
			name="TestUser",
			url="http://asdf.com",
			client_type=0,
			redirect_uri="http://fdsa.com",
			client_id = 'fdasasdfasdf',
			client_secret = 'asdflkjhlkjasdlfjkhasjlksjldkjf',
		)
		self.client.save()

	def test_get(self):
		text = get(self.client, self.repository, wikiURL)

		self.assertIsInstance(text, Text)

		text.content.delete()

	def tearDown(self):
		self.client.delete()
		self.user.delete()
		self.repository.delete()


class TestGetJARS(unittest.TestCase):
	def setUp(self):
		self.repository = Repository(
			name='TestRepository',
			manager='JARS',
			endpoint='http://localhost:8002',
		)
		self.repository.save()

		self.user = User(
			username = 'Bob',
			password = 'bobpass',
		)
		self.user.save()

		self.client = Client(
			user=self.user,
			name="TestUser",
			url="http://asdf.com",
			client_type=0,
			redirect_uri="http://fdsa.com",
			client_id = 'fdasasdfasdf',
			client_secret = 'asdflkjhlkjasdlfjkhasjlksjldkjf',
		)
		self.client.save()

	def test_get(self):
		kwargs = {
			'token': '050814a54ac5c81b990140c3c43278031d391676',
		}
		text = get(self.client, self.repository, jars_uri, **kwargs)

		self.assertIsInstance(text, Text)

		text.content.delete()

	def tearDown(self):
		self.client.delete()
		self.user.delete()
		self.repository.delete()


if __name__ == "__main__":
	unittest.main()
