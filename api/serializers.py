from rest_framework import serializers, exceptions
from django.db.utils import IntegrityError
from api.models import TaskDef, Task, PRIORITY_CHOICES

class UniqueTaskConflict(exceptions.APIException):
    status_code = 409
    default_detail = 'Task `unique` field conflict'

class TaskDefSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False, max_length=255)
    title = serializers.CharField(required=False, allow_null=True, allow_blank=False, max_length=255)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=False, max_length=2048)
    default_timeout = serializers.IntegerField(required=False)
    max_attempts = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        try:
            return TaskDef.objects.create(**validated_data)
        except IntegrityError:
            raise exceptions.ValidationError({'name': '"{name}" already taken.'.format(**validated_data)})

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.default_timeout = validated_data.get('default_timeout', instance.default_timeout)
        instance.max_attempts = validated_data.get('max_attempts', instance.max_attempts)
        instance.save()
        return instance

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    task_def = serializers.PrimaryKeyRelatedField(required=True, queryset=TaskDef.objects.all())
    status = serializers.CharField(read_only=True)
    worker_id = serializers.CharField(read_only=True, required=False, max_length=255)
    locked_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    priority = serializers.ChoiceField(required=False, choices=PRIORITY_CHOICES)
    unique = serializers.CharField(required=False, max_length=255)
    run_at = serializers.DateTimeField(required=False, format='iso-8601', input_formats=['iso-8601'])
    started_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])
    completed_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])
    failed_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])
    data = serializers.JSONField(required=False, allow_null=True)
    attempts = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        try:
            return Task.objects.create(**validated_data)
        except IntegrityError:
            raise UniqueTaskConflict()

    def update(self, instance, validated_data):
        failed_at = validated_data.get('failed_at', None)
        completed_at = validated_data.get('completed_at', None)
        
        if failed_at == None and completed_at != None:
            instance.status = 'complete'
        elif failed_at != None and completed_at == None:
            if instance.attempts >= instance.task_def.max_attempts:
                instance.status = 'failed'
            else:
                instance.status = 'failed_retrying'
        elif failed_at != None and completed_at != None:
            raise exceptions.ValidationError('`failed_at` and `completed_at` cannot be both non-null at the same time.')

        instance.worker_id = validated_data.get('worker_id', instance.priority)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.started_at = validated_data.get('started_at', instance.started_at)
        instance.completed_at = completed_at
        instance.failed_at = failed_at
        instance.data = validated_data.get('data', instance.data)
        instance.save()
        return instance
