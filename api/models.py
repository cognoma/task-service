from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.postgres import fields as postgresfields

STATUS_CHOICES = (
    ("pending_queue", "Pending Queue"),
    ("scheduled", "Scheduled"),
    ("queued", "Queued"),
    ("in_progress", "In Progress"),
    ("failed_retrying", "Failed - Retrying"),
    ("dequeued", "Dequeued"),
    ("failed", "Failed"),
    ("completed", "Completed")
)

PRIORITY_CHOICES = (
    ("critical", "Critical"),
    ("high", "High"),
    ("normal", "Normal"),
    ("low", "Low")
)

class TaskDef(models.Model):
    class Meta:
        db_table = "task_defs"

    name = models.CharField(null=False, max_length=255, unique=True) # ex "classifier_search"
    priority_levels = postgresfields.ArrayField(models.CharField(max_length=8, choices=PRIORITY_CHOICES))
    title = models.CharField(null=True, max_length=255, blank=False) # ex "Classifier Search"
    description = models.CharField(null=True, max_length=2048, blank=False) # optional description
    default_timeout = models.IntegerField(default=600) # default timeout, in seconds
    max_attempts = models.IntegerField(default=1) # max number of times this job can attempt to run
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(models.Model):
    class Meta:
        db_table = "tasks"

    task_def = models.ForeignKey(TaskDef)
    lock_id = models.CharField(null=True, max_length=255) # message or lock id from queue
    status = models.CharField(choices=STATUS_CHOICES, max_length=17)
    received_at = models.DateTimeField(null=True)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=8, default="normal")
    unique = models.CharField(null=True, max_length=255)
    run_at = models.DateTimeField(default=timezone.now)
    run_every = models.CharField(null=True, max_length=255) # cron string for recurring jobs
    recurring_run_enabled = models.NullBooleanField()
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
    data = postgresfields.JSONField(null=True)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
