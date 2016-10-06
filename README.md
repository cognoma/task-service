# Cognoma task-service

This repository houses the service, accessible by HTTP RESTful API, responsable for manageing backround tasks within the Cognoma application backend.

## Getting started

Make sure to fork [this repository on
 +GitHub](https://github.com/cognoma/task-service "cognoma/task-service on
 +GitHub") first.

### Prerequisites
- Python 3 - tested with Python 3.5.1
- virtualenv - tested on 15.0.2
- Postgres 9.5.x - tested on Postgres 9.5.2

### Setup Postgres

```sh
CREATE USER app WITH PASSWORD 'password';
CREATE DATABASE cognoma;
CREATE SCHEMA task_service;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA task_service TO app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA task_service TO app;
ALTER DEFAULT PRIVILEGES IN SCHEMA task_service GRANT ALL PRIVILEGES ON TABLES TO app;
ALTER DEFAULT PRIVILEGES IN SCHEMA task_service GRANT ALL PRIVILEGES ON SEQUENCES TO app;
```

### Setup up the API

```sh
USERNAME=your_github_handle # Change to your GitHub Handle
git clone git@github.com:${USERNAME}/task-service.git
cd task-service
virtualenv --python=python3 env
source env/bin/activate
pip install --requirement requirements.txt
python manage.py migrate
python manage.py runserver
```

The server should start up at http://127.0.0.1:8000/, see the [API docs](https://github.com/cognoma/task-service/blob/master/doc/api.md).
