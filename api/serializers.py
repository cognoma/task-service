from rest_framework import serializers
from api.models import TaskDef, Task, STATUS_CHOICES, PRIORITY_CHOICES

class TaskDefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, allow_blank=False, max_length=255)
    priority_levels = serializers.ListField(
        child=serializers.ChoiceField(choices=PRIORITY_CHOICES)
    )
    title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=False, max_length=2048)
    default_timeout = serializers.IntegerField(required=False)
    max_attempts = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        return TaskDef.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.default_timeout = validated_data.get('default_timeout', instance.default_timeout)
        instance.max_attempts = validated_data.get('max_attempts', instance.max_attempts)
        instance.save()
        return instance

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    task_def = serializers.PrimaryKeyRelatedField(required=True, queryset=TaskDef.objects.all())
    lock_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    received_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    priority = serializers.ChoiceField(required=False, choices=STATUS_CHOICES)
    unique = serializers.CharField(required=False, max_length=255)
    run_at = serializers.DateTimeField(required=False, format='iso-8601', input_formats=['iso-8601'])
    run_every = serializers.CharField(required=False, max_length=255)
    recurring_run_enabled = serializers.NullBooleanField(required=False, )
    started_at = serializers.DateTimeField(required=False, format='iso-8601', input_formats=['iso-8601'])
    completed_at = serializers.DateTimeField(required=False, format='iso-8601', input_formats=['iso-8601'])
    failed_at = serializers.DateTimeField(required=False, format='iso-8601', input_formats=['iso-8601'])
    data = serializers.JSONField(required=False)
    attempts = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.priority = validated_data.get('priority', instance.priority)
        instance.run_at = validated_data.get('run_at', instance.run_at)
        instance.run_every = validated_data.get('run_every', instance.run_every)
        instance.recurring_run_enabled = validated_data.get('recurring_run_enabled', instance.recurring_run_enabled)
        instance.started_at = validated_data.get('started_at', instance.started_at)
        instance.completed_at = validated_data.get('completed_at', instance.completed_at)
        instance.failed_at = validated_data.get('failed_at', instance.failed_at)
        instance.data = validated_data.get('data', instance.data)
        instance.save()
        return instance
