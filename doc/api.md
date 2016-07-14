# Task Service API


## Overview

The task service's responsiblity is managing automated background tasks. It has a data model that allows for the central registration and reporting of automated tasks. Both processes that queue tasks and work on tasks communicate with the task service via an HTTP RESTful API.

Workers can be any process that can communicate with an HTTP service. Typically, a worker long polls the HTTP API until a task becomes available. A [python client](https://github.com/cognoma/python-task-client) class is available, others may be developed depending on need.

## Schemas

### Task Definition (/task-defs)

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto Incrementing. | Y |
| name | string | The task's code friendly name. Ex classifier_search. Max 255.| N |
| title | string | The task's display friendly name. Ex "Classifier Search". Max 255. | N |
| description | string | Text describing details of the task. Max 2048. | N |
| default_timeout | integer | The default timeout for the task, in seconds. When a worker has stopped reporting on the task and the task has not completed or failed, the task is given to another worker. Default 600. | N |
| max_attempts | integer | The maxium number of times a task can be attempted. Default 1. | N |
| priority_levels | string array | The priority levels for this task. Default ["normal"] | N |


### Task (/tasks)

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto Incrementing. | Y |
| task\_def\_id | integer | Foreign Key referencing the task definition. | N |
| task\_def\_name | string | Task definition's name. Included in rest response automatically. | Y |
| lock_id | string | The message receipt or other identifying handle from the queue. Set by service. | Y |
| status | string | The status of the task. Enumeration, options below. Set by service. | Y |
| received_at | datetime | The last time a worker was issued a task. Set by service. | Y |
| priority | string | The task's priority. Enumeration, options below. | N |
| unique | string | Optional unique string set by queuer, which prevents tasks from being queued multiple times. | N |
| data | map | Key/value map containing input parameters for the task. Stored as JSONB in Postgres. | N |
| run_at | datetime | When to run the task. Defaults to now. | N |
| run_every | string | Optional Cron string for recurring tasks. Next run_at is calculated using this. | N |
| started_at | datetime | When the task was started | N |
| completed_at | datetime | When the task completed, this is also how a worker communicates success. | N |
| failed_at | datetime | When the task failed, this is also how a worker communicates failure. | N |
| error_message | string | When failure has occured, a user friendly error message for display. | N |
| attempts | integer | The number of times the task has been attempted so far. Used for retrying. Set by service. | Y |

#### Task Status (status)
 - pending_queue - "Pending Queue" - Usually only in this state for a short time, between saving the task to the DB and adding it to the queue. This helps with recovery when queue is down.
 - scheduled - Scheduled - Task is scheduled for a future datetime and will be queued then.
 - queued - Queued - Task is in the queue.
 - in_progress - In Progress - Task is in progress, being worked on by a worker.
 - failed_retrying - Failed - Retrying - Task failed and is being retried.
 - dequeued - Dequeued - Task has been removed from the queue and will not be worked on.
 - failed - Failed - Task has failed.
 - completed - Completed - Task has completed.

#### Task Priorities (priority)
 - citrical
 - high
 - normal
 - low

A unique partial index exists on `unique`. It maintains a unique index only on tasks that have a status of pending\_queue, scheduled, queued, or in\_progress.

## Example Requests

### Create task def - registering a new task

`POST /task-defs`

POST Data

    {
        name: "classifier_search",
        title: "Classifier Search"
    }
    
Response

    {
        id: 1,
        name: "classifier_search",
        priority_levels: ["normal"],
        title: "Classifier Search",
        default_timeout: 600,
        max_attempts: 1
    }

### Queue a task

`POST /tasks`

POST Data

    {
        task_def_id: 1,
        unique: "cookie-user-32323-geneset-235",
        data: {
        	algorithm: "svm"
        	...
        }
    }
    
Response

    {
        id: 238,
        task_def_id: 1,
        task_def_name: "classifier_search",
        status: "queued",
        priority: "normal",
        unique: "cookie-user-32323-geneset-235",
        data: {
        	algorithm: "svm"
        	...
        },
        run_at: "2016-07-14T00:57:51+00:00",
        attempts: 0
    }
    
### Get a task issued to you - for workers

`GET /tasks?tasks=classifier_search,geneset_status_email&n=1&timeout=20`

Query Parameters

- tasks - List of task defs the worker can perform.
- n - Number of tasks to fetch.
- timeout - HTTP long polling timeout. How long to wait for a task.

Response

    {
        id: 238,
        task_def_id: 1,
        task_def_name: "classifier_search",
        lock_id: "j4qtjq43fu3utr034tu0t4t0uu0uja3ew",
        status: "in_progress",
        received_at: "2016-07-14T00:57:51+00:00",
        priority: "normal",
        unique: "cookie-user-32323-geneset-235",
        data: {
        	algorithm: "svm"
        	...
        },
        run_at: "2016-07-14T00:57:51+00:00",
        attempts: 1
    }
    
### Get the status of a task

`GET /tasks/238`

Response

    {
        id: 238,
        task_def_id: 1,
        task_def_name: "classifier_search",
        lock_id: "j4qtjq43fu3utr034tu0t4t0uu0uja3ew",
        status: "in_progress",
        received_at: "2016-07-14T00:57:51+00:00",
        priority: "normal",
        unique: "cookie-user-32323-geneset-235",
        data: {
        	algorithm: "svm"
        	...
        },
        run_at: "2016-07-14T00:57:51+00:00",
        attempts: 1
    }

### Get a list of running tasks

`GET /tasks?status=in_progress`

Response

    [{
        id: 238,
        task_def_id: 1,
        task_def_name: "classifier_search",
        lock_id: "j4qtjq43fu3utr034tu0t4t0uu0uja3ew",
        status: "in_progress",
        received_at: "2016-07-14T00:57:51+00:00",
        priority: "normal",
        unique: "cookie-user-32323-geneset-235",
        data: {
        	algorithm: "svm"
        	...
        },
        run_at: "2016-07-14T00:57:51+00:00",
        attempts: 1
     },
     ...
    ]
    
### Touch a task - resetting it's timeout

`POST /tasks/238/touch`

### Release a task - let another worker pick it up

`POST /tasks/238/release`

### Dequeue a task - cancel it

`POST /tasks/238/dequeue`