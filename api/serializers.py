from rest_framework import serializers
from api.models import TaskDef

class TaskDefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, allow_blank=False, max_length=255)
    priority_levels = serializers.ListField(
        child=serializers.CharField(allow_blank=False, max_length=255)
    )
    title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=False, max_length=2048)
    default_timeout = serializers.IntegerField(required=False)
    max_attempts = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(read_only=True,format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True,format='iso-8601')

    def create(self, validated_data):
        return TaskDef.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.default_timeout = validated_data.get('default_timeout', instance.default_timeout)
        instance.max_attempts = validated_data.get('max_attempts', instance.max_attempts)
        instance.save()
        return instance
