from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^task-defs/?$', views.TaskDefList.as_view()),
    url(r'^task-defs/(?P<name>[a-z0-9\-_]+)$', views.TaskDefRetrieveUpdate.as_view()),
    url(r'^tasks/?$', views.TaskList.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)$', views.TaskRetrieveUpdate.as_view())
]
