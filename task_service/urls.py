from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^task-defs/?$', views.task_def_list),
    url(r'^task-defs/(?P<id>[0-9]+)$', views.task_def_detail),
    url(r'^tasks/?$', views.task_list),
    url(r'^tasks/(?P<id>[0-9]+)$', views.task_detail)
]
