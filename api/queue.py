from api.models import TaskDef, Task


# join to task_defs for specific timeout and max_attempts?
get_task_sql = """
WITH nextTasks as (
    SELECT id
    FROM task_service.tasks
    JOIN task_service.task_defs
    ON task_service.tasks.task_def_name = task_service.task_defs.name
    WHERE (status = 'queued' OR
            (status IN ('in_progress','failed_retrying')
                 AND (received_at < (now() - INTERVAL '1 second' * task_service.task_defs.default_timeout))
                 AND attempts < task_service.task_defs.max_attempts))
        AND task_def_name IN (%s)
        AND run_at <= now()
    ORDER BY
        CASE WHEN priority = 'critical'
             THEN 1
             WHEN priority = 'high'
             THEN 2
             WHEN priority = 'normal'
             THEN 3
             WHEN priority = 'low'
             THEN 4
        END,
        run_at
    LIMIT %status
    FOR UPDATE SKIP LOCKED
)
UPDATE task_service.tasks SET
    status = 'in_progress',
    received_at = now(),
    started_at = now(),
    attempts = attempts + 1
FROM nextTasks
WHERE task_service.tasks.id = nextTasks.id
RETURNING task_service.tasks.*;

"""

def get_task(task_names, limit=1):
    Task.objects.raw(Queue.get_task_sql, [])
