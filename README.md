# Cognoma task-service

This repository houses the service, accessible by HTTP RESTful API, responsable for manageing backround tasks within the Cognoma application backend.

## Getting started

Make sure to fork [this repository on
 +GitHub](https://github.com/cognoma/task-service "cognoma/task-service on
 +GitHub") first.

### Prerequisites

- Docker - tested with 1.12.1
- Docker Compose - tested with 1.8.0

### Setup Postgres

```sh
docker-compose up
```

Sometimes the postgres image takes a while to load on first run and the Django server starts up first. If this happens just ctrl+C and rerun `docker-compose up`

The code in the repository is also mounted as a volume in the task-service container. This means you can edit code on your host machine, using your favorite editor, and the django server will automatically restart to reflect the code changes.

The server should start up at http://localhost:8080/, see the [API docs](https://github.com/cognoma/task-service/blob/master/doc/api.md).

## Running tests locally

Make sure the service is up first using `docker-compose up` then run:

```sh
docker-compose exec task python manage.py test
```