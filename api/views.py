import django_filters
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from api.models import TaskDef, Task
from api.serializers import TaskDefSerializer, TaskSerializer
from api import queue

# TaskDef

class TaskDefFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    class Meta:
        model = TaskDef
        fields = ['name', 'created_at', 'updated_at']

class TaskDefList(generics.ListCreateAPIView):
    queryset = TaskDef.objects.all()
    serializer_class = TaskDefSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TaskDefFilter
    ordering_fields = ('name','created_at','updated_at')
    ordering = ('name',)

class TaskDefRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = TaskDef.objects.all()
    serializer_class = TaskDefSerializer
    lookup_field = 'name'

# Task

class TaskFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    locked_at__gte = django_filters.IsoDateTimeFilter(name='locked_at', lookup_expr='gte')
    locked_at__lte = django_filters.IsoDateTimeFilter(name='locked_at', lookup_expr='lte')

    run_at__gte = django_filters.IsoDateTimeFilter(name='run_at', lookup_expr='gte')
    run_at__lte = django_filters.IsoDateTimeFilter(name='run_at', lookup_expr='lte')

    started_at__gte = django_filters.IsoDateTimeFilter(name='started_at', lookup_expr='gte')
    started_at__lte = django_filters.IsoDateTimeFilter(name='started_at', lookup_expr='lte')

    completed_at__gte = django_filters.IsoDateTimeFilter(name='completed_at', lookup_expr='gte')
    completed_at__lte = django_filters.IsoDateTimeFilter(name='completed_at', lookup_expr='lte')

    failed_at__gte = django_filters.IsoDateTimeFilter(name='failed_at', lookup_expr='gte')
    failed_at__lte = django_filters.IsoDateTimeFilter(name='failed_at', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['id',
                  'task_def',
                  'status',
                  'worker_id',
                  'locked_at',
                  'priority',
                  'unique',
                  'run_at',
                  'started_at',
                  'completed_at',
                  'failed_at',
                  'attempts',
                  'created_at',
                  'updated_at']

class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TaskFilter
    ordering_fields = ('name',
                       'locked_at',
                       'run_at',
                       'started_at',
                       'completed_at',
                       'failed_at',
                       'attempts',
                       'created_at',
                       'updated_at')
    ordering = ('id',)

class TaskRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'id'

class PullQueue(APIView):
    def get(self, request, format=None):
        if 'tasks' not in request.query_params:
            raise ParseError('`tasks` query parameter required')

        if 'limit' in request.query_params:
            limit = request.query_params['limit'] ## TODO: integer validation
        else:
            limit = 1

        ## TODO: allow for comma separated task list?
        raw_tasks = queue.get_tasks(request.query_params.getlist('tasks'), limit)

        tasks = []
        for task in raw_tasks:
            serializer = TaskSerializer(task)
            tasks.append(serializer.data)

        return Response(tasks)
