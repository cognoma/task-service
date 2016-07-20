from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import TaskDef, Task
from api.serializers import TaskDefSerializer, TaskSerializer

@api_view(['GET', 'POST'])
def task_def_list(request):
    if request.method == 'GET':
        task_defs = TaskDef.objects.all()
        serializer = TaskDefSerializer(task_defs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskDefSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def task_def_detail(request, id):
    try:
        task_def = TaskDef.objects.get(pk=pk)
    except TaskDef.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskDefSerializer(task_def)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskDefSerializer(task_def, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def task_detail(request, id):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
