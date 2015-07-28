"""eratosthenes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^get/(?P<repository_id>[0-9]+)/(?P<uri>.*)/$', views.get),
    url(r'^repositories/(?P<repository_id>[0-9]+)/texts/$', views.repository_texts),
    url(r'^repositories/(?P<repository_id>[0-9]+)/browse/$', views.repository_browse),
    url(r'^repositories/(?P<repository_id>[0-9]+)/collections/(?P<collection_id>[0-9]+)/$', views.repository_collection_browse),
    url(r'^repositories/(?P<repository_id>[0-9]+)/collections/$', views.repository_collections),
    url(r'^repositories/(?P<repository_id>[0-9]+)/$', views.repository),
    url(r'^repositories/', views.repositories),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
]
