from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres import fields as postgresfields

class TaskDef(models.Model):
    class Meta:
        db_table = "task_defs"

    name = models.CharField(max_length=255) # ex "classifier_search"
    priority_levels = postgresfields.ArrayField(models.CharField(max_length=255))
    title = models.CharField(max_length=255) # ex "Classifier Search"
    description = models.CharField(max_length=2048) # optional description
    default_timeout = models.IntegerField(default=600) # default timeout, in seconds
    max_attempts = models.IntegerField(default=1) # max number of times this job can attempt to run
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(models.Model):
    class Meta:
        db_table = "tasks"

    task_def_id = models.ForeignKey(TaskDef)
    lock_id = models.CharField(max_length=255) # message or lock id from queue
    status = models.CharField(
        choices=(
            ("pending_queue", "Pending Queue"),
            ("scheduled", "Scheduled"),
            ("queued", "Queued"),
            ("in_progress", "In Progress"),
            ("failed_retrying", "Failed - Retrying"),
            ("dequeued", "Dequeued"),
            ("failed", "Failed"),
            ("completed", "Completed")
        ),
        max_length=17
    )
    received_at = models.DateTimeField()
    priority = models.CharField(
        choices=(
            ("critical", "Critical"),
            ("high", "High"),
            ("normal", "Normal"),
            ("low", "Low")
        ),
        max_length=8
    )
    unique = models.CharField(max_length=255)
    run_at = models.DateTimeField()
    run_every = models.CharField(max_length=255) # cron string for recurring jobs
    recurring_run_enabled = models.NullBooleanField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    failed_at = models.DateTimeField()
    data = postgresfields.JSONField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
