from django.db import models
from managers import repositoryManagers
from django.contrib.auth.models import User

class Repository(models.Model):
    name = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    manager = models.CharField(max_length=100, choices=repositoryManagers)

    def getManager(self, **kwargs):
        return dict(repositoryManagers)[self.manager](self.endpoint, **kwargs)

    def browse(self, **kwargs):
        """
        Retrieve a list of resources.
        """

        manager = self.getManager(**kwargs)
        return manager.browse()

    def getCollections(self, **kwargs):
        manager = self.getManager(**kwargs)
        collections = manager.collections()

        instances = []
        for collection in collections:
            instance, created = Collection.objects.get_or_create(
                uri=collection['uri'],
                defaults={
                    'title': collection['title'],
                    'remote_id': collection['id'],
                    'source': self,
                })
            instances.append(instance)
        return instances


class Collection(models.Model):
    uri = models.CharField(max_length=255, unique=True)

    title = models.CharField(max_length=255)
    remote_id = models.CharField(max_length=255)
    source = models.ForeignKey('Repository', related_name='collections')
    resources = models.ManyToManyField('Resource', related_name='partOf')

    def getResources(self, **kwargs):
        """
        Retrieve a list of resources in a collection.
        """

        manager = self.source.getManager(**kwargs)
        resources = manager.collection(self.remote_id)
        instances = []
        for resource in resources:
            instance, created = Resource.objects.get_or_create(
                uri=resource['uri'],
                defaults={
                    'title': resource['title'],
                    'source': self.source,
                })
            self.resources.add(instance)
            instances.append(instance)
        return instances


class Resource(models.Model):
    source = models.ForeignKey('Repository')

    uri = models.CharField(max_length=255, unique=True)
    """Should be sufficient to retrieve the Resource from its source."""

    title = models.CharField(max_length=255, blank=True, null=True)
    """Original title of the Resource, for display, if available."""

    created = models.DateField(blank=True, null=True)
    """The date that the original resource was created (e.g. published)."""

    content = models.FileField()
    """Eratosthenes is totally agnostic about content."""

    contentType = models.CharField(max_length=255, blank=True, null=True)
    """Ok, maybe not entirely agnostic."""

    retrieved = models.BooleanField(default=False)
    """Whether or not the content of this Resource has been retrieved."""

    retrievedOn = models.DateTimeField(blank=True, null=True)
    """The date/time when this Resource was retrieved from its ``source``."""

    retrievedBy = models.ForeignKey(User, blank=True, null=True)
