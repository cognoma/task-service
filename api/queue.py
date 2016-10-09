from django.db import connection

from api.models import TaskDef, Task

# join to task_defs for specific timeout and max_attempts?
get_task_sql = """
WITH nextTasks as (
    SELECT id
    FROM task_service.tasks
    JOIN task_service.task_defs
    ON task_service.tasks.task_def_name = task_service.task_defs.name
    WHERE
       task_def_name = ANY(%s)
       AND run_at <= NOW()
       AND (status = 'queued' OR
           (status = 'in_progress' AND
            (NOW() > (locked_at + INTERVAL '1 second' * task_service.task_defs.default_timeout))) OR
           (status = 'failed_retrying' AND
            attempts < task_service.task_defs.max_attempts))
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
    LIMIT %s
    FOR UPDATE SKIP LOCKED
)
UPDATE task_service.tasks SET
    status = 'in_progress',
    locked_at = now(),
    started_at = now(),
    attempts = attempts + 1
FROM nextTasks
WHERE task_service.tasks.id = nextTasks.id
RETURNING task_service.tasks.*;
"""
## TODO: only update attempts on fail?

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

## TODO: set worker_id
def get_tasks(task_names, limit=1):
    with connection.cursor() as cursor:
        cursor.execute(get_task_sql, [task_names, limit])
        raw_tasks = dictfetchall(cursor)

    for raw_task in raw_tasks:
        task_name = raw_task.pop('task_def_name')
        raw_task['task_def'] = TaskDef(name=task_name)

    tasks = []
    for raw_task in raw_tasks:
        tasks.append(Task(**raw_task))

    return tasks
