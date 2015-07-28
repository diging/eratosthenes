from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from models import Repository, Text

import tempfile

class OpenTemp(object):
	def __enter__(self):
		self.f = tempfile.TemporaryFile()
		self.file = File(self.f)
		return self.file

	def __exit__(self, type, value, traceback):
		self.f.close()


def get(client, repository, uri, **kwargs):
	"""
	Retrieve a :class:`.Text` from a ``repository`` by its ``uri``.
	"""

	try:
		text = Text.objects.get(uri=uri)
	except ObjectDoesNotExist:
		manager = repository.getManager(**kwargs)
		textData = manager.get(uri)

		with OpenTemp() as content:
			content.write(textData['content'].encode('utf-8'))
			text = Text(
				uri=uri,
				title=textData.get('title', None),
				content=content,
				contentType=textData.get('content-type', 'unknown'),
				source=repository,
				retrievedBy=client
			)
			text.save()
	return text
