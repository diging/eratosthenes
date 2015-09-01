from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.serializers import serialize

from rest_framework import viewsets, serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from models import Repository, Resource, Collection
import json
import tempfile

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        try:
            content = JSONRenderer().render(data)
        except TypeError:
            noiter = False
            if not hasattr(data, '__iter__'):
                noiter = True
                data = [data]
            content = serialize('json', data)
            if noiter:
                content = content[1:-1]
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class OpenTemp(object):
    def __enter__(self):
        self.f = tempfile.TemporaryFile()
        self.file = File(self.f)
        return self.file

    def __exit__(self, type, value, traceback):
        self.f.close()


def json_response(func):
    def response(request, **kwargs):
        data = func(request, **kwargs)
        return JSONResponse(data, status=201)#, content_type='application/json')
    return response


def attach_content(resource, result):
    with OpenTemp() as content:
        content.write(result['content'].encode('utf-8'))
        resource.content = content
        resource.contentType = result.get('content-type', 'unknown')
        resource.title = result.get('title', 'unknown')
        resource.save()
    return resource


def retrieve(request, uri):
    resource = None
    try:
        resource = Resource.objects.get(uri=uri)
        if not resource.retrieved:
            result = resource.source.getManager().get(uri)

    except ObjectDoesNotExist:
        
        result = None
        for repository in Repository.objects.all():
            result = repository.getManager().get(uri)
            if result is not None:
                if result is not None:
                    resource = Resource(
                        uri = uri,
                        source = repository,
                    )
                    resource.save()
                    break
    if resource is None:
        return JSONResponse([])

    if not resource.retrieved and result is not None:
        resource = attach_content(resource, result)

    return JSONResponse(resource)

def get_content(request, uri):
    try:
        resource = Resource.objects.get(uri=uri)
        if not resource.retrieved:
            result = resource.source.getManager().get(uri)

    except ObjectDoesNotExist:
        result = None
        for repository in Repository.objects.all():
            result = repository.getManager().get(uri)
            if result is not None:
                resource = Resource(
                    uri = uri,
                    source = repository,
                )
                resource.save()
                break

    if not resource.retrieved and result is not None:
        resource = attach_content(resource, result)

    response = HttpResponse(resource.content, content_type=resource.contentType)
    response['Content-Disposition'] = 'attachment; filename="'+resource.title+'"'
    return response


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = ('url', 'uri', 'id', 'title', 'created', 'contentType',
                  'retrieved', 'retrievedOn', 'retrievedBy', 'source')

class ResourceTerseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = ('url', 'uri', 'id', 'title')


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    resources = ResourceTerseSerializer(many=True, read_only=True)


    class Meta:
        model = Collection
        fields = ('url', 'title', 'uri', 'remote_id', 'id', 'source', 'resources')

    def __init__(self, instance=None, *args, **kwargs):
        if type(instance) is Collection:
            instance.getResources()
        return super(CollectionSerializer, self).__init__(instance, *args, **kwargs)

class CollectionTerseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ('url', 'uri', 'id', 'title')


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    collections = CollectionTerseSerializer(many=True, read_only=True)

    class Meta:
        model = Repository
        fields = ('url', 'name', 'id', 'manager', 'endpoint', 'collections')

    def __init__(self, instance=None, *args, **kwargs):
        print instance, type(instance)
        if type(instance) is Repository:
            instance.getCollections()
        return super(RepositorySerializer, self).__init__(instance, *args, **kwargs)


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
