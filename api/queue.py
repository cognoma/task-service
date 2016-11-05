from django.db import connection

from api.models import TaskDef, Task

get_task_sql = """
WITH nextTasks as (
    SELECT id, status, started_at
    FROM tasks
    JOIN task_defs
    ON tasks.task_def_name = task_defs.name
    WHERE
       task_def_name = ANY(%s)
       AND run_at <= NOW()
       AND (status = 'queued' OR
           (status = 'in_progress' AND
            (NOW() > (locked_at + INTERVAL '1 second' * task_defs.default_timeout))) OR
           (status = 'failed_retrying' AND
            attempts < task_defs.max_attempts))
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
UPDATE tasks SET
    status = 'in_progress',
    worker_id = %s,
    locked_at = now(),
    started_at =
        CASE WHEN nextTasks.started_at = null
             THEN now()
             ELSE null
        END,
    attempts =
        CASE WHEN nextTasks.status = 'in_progress'
             THEN attempts
             ELSE attempts + 1
        END
FROM nextTasks
WHERE tasks.id = nextTasks.id
RETURNING tasks.*;
"""

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_tasks(task_names, worker_id, limit=1):
    with connection.cursor() as cursor:
        cursor.execute(get_task_sql, [task_names, limit, worker_id])
        raw_tasks = dictfetchall(cursor)

    for raw_task in raw_tasks:
        task_name = raw_task.pop('task_def_name')
        raw_task['task_def'] = TaskDef(name=task_name)

    tasks = []
    for raw_task in raw_tasks:
        tasks.append(Task(**raw_task))

    return tasks
