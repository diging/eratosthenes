from django.db import models
from managers import repositoryManagers
from provider.oauth2.models import Client

class Repository(models.Model):
	name = models.CharField(max_length=255)
	endpoint = models.CharField(max_length=255)
	manager = models.CharField(max_length=100, choices=repositoryManagers)

	def getManager(self, **kwargs):
		return dict(repositoryManagers)[self.manager](self.endpoint, **kwargs)

	def browse(self, **kwargs):
		"""
		Retrieve a list of texts.
		"""

		manager = self.getManager(**kwargs)
		return manager.browse()

	def collections(self, **kwargs):
		"""
		Retrieve a list of collections.
		"""

		manager = self.getManager(**kwargs)
		return manager.collections()

	def collection(self, collection_id, **kwargs):
		"""
		Retrieve a list of texts in a collection.
		"""

		manager = self.getManager(**kwargs)
		return manager.collection(collection_id)


class Text(models.Model):
	source = models.ForeignKey('Repository')

	uri = models.CharField(max_length=255, unique=True)
	"""Should be sufficient to retrieve the Text from its source."""

	title = models.CharField(max_length=255, blank=True, null=True)
	"""Original title of the Text, for display, if available."""

	created = models.DateField(blank=True, null=True)
	"""The date that the original resource was created (e.g. published)."""

	content = models.FileField()
	"""Eratosthenes is totally agnostic about content."""

	contentType = models.CharField(max_length=255)
	"""Ok, maybe not entirely agnostic."""

	retrieved = models.DateTimeField(auto_now_add=True)
	"""The date/time when this Text was retrieved from its ``source``."""

	retrievedBy = models.ForeignKey(Client)
