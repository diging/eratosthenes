from django.http import HttpResponse
from django.core import serializers
from django.conf import settings

from models import Repository, Text
from tasks import get
import json

def json_response(func):
	def response(request, **kwargs):
		data = func(request, **kwargs)
		try:
			rdata = serializers.serialize("json", data)
		except AttributeError:
			rdata = json.dumps(data)
		return HttpResponse(rdata, content_type='application/json')
	return response


# def get(request, respository_id, uri):
# 	repository = Repository.objects.get(pk=repository_id)
	

@json_response
def repositories(request):
	"""
	List of repositories.
	"""

	return Repository.objects.all()


@json_response
def repository(request, repository_id):
	return Repository.objects.filter(pk=repository_id)


@json_response
def repository_texts(request, repository_id):
	return Text.objects.filter(source=repository_id)


@json_response
def repository_browse(request, repository_id):
	repository = Repository.objects.get(pk=repository_id)
	return repository.browse()


@json_response
def repository_collections(request, repository_id):
	repository = Repository.objects.get(pk=repository_id)
	return repository.collections()


@json_response
def repository_collection_browse(request, repository_id, collection_id):
	repository = Repository.objects.get(pk=repository_id)
	return repository.collection(collection_id)
