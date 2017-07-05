from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^task-defs/?$', views.TaskDefList.as_view()),
    url(r'^task-defs/(?P<name>[a-z0-9\-_]+)/?$', views.TaskDefRetrieveUpdate.as_view()),

    url(r'^tasks/queue/?$', views.PullQueue.as_view()),

    url(r'^tasks/?$', views.TaskList.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)/?$', views.TaskRetrieveUpdate.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)/touch/?$', views.TouchTask.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)/release/?$', views.ReleaseTask.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)/dequeue/?$', views.DequeueTask.as_view()),
    url(r'^tasks/(?P<id>[0-9]+)/complete/?$', views.CompleteTask.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
