from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.postgres import fields as postgresfields

STATUS_CHOICES = (
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

    name = models.CharField( # ex "classifier_search"
        primary_key=True,
        max_length=255,
        validators=[
            RegexValidator(
                regex='^[a-z0-9\-_]+$',
                message='Task definition name can only contain lowercase alphanumeric charaters, dashes, and underscores.',
            )
        ]
    )
    priority_levels = postgresfields.ArrayField(models.CharField(max_length=8, choices=PRIORITY_CHOICES), default=['normal'])
    title = models.CharField(null=True, max_length=255, blank=False) # ex "Classifier Search"
    description = models.CharField(null=True, max_length=2048, blank=False) # optional description
    default_timeout = models.IntegerField(default=600) # default timeout, in seconds
    max_attempts = models.IntegerField(default=1) # max number of times this job can attempt to run
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(models.Model):
    class Meta:
        db_table = "tasks"

    task_def = models.ForeignKey(TaskDef, db_column="task_def_name")
    status = models.CharField(choices=STATUS_CHOICES, max_length=17, default='queued')
    worker_id = models.CharField(null=True, max_length=255)
    ## make dispatched_at?
    received_at = models.DateTimeField(null=True)
    ## add queued_at? redundent with created_at?
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=8, default="normal") ## TODO: validate priority against task_def
    unique = models.CharField(null=True, max_length=255)
    run_at = models.DateTimeField(default=lambda: timezone.now())
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
    data = postgresfields.JSONField(null=True)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
