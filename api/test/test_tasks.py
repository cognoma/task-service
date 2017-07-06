from datetime import datetime
from unittest.mock import patch

from rest_framework.test import APITestCase, APIClient

task_keys = ['id',
             'task_def',
             'status',
             'worker_id',
             'locked_at',
             'priority',
             'unique',
             'run_at',
             'started_at',
             'completed_at',
             'failed_at',
             'data',
             'attempts',
             'created_at',
             'updated_at']

class TaskTests(APITestCase):
    def setUp(self):
        client = APIClient()

        self.token = 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXJ2aWNlIjoiY29yZSJ9.HHlbWMjo-Y__DGV0DAiCY7u85FuNtY8wpovcZ9ga-oCsLdM2H5iVSz1vKiWK8zxl7dSYltbnyTNMxXO2cDS81hr4ohycr7YYg5CaE5sA5id73ab5T145XEdF5X_HXoeczctGq7X3x9QYSn7O1fWJbPWcIrOCs6T2DrySsYgjgdAAnWnKedy_dYWJ0YtHY1bXH3Y7T126QqVlQ9ylHk6hmFMCtxMPbuAX4YBJsxwjWpMDpe13xbaU0Uqo5N47a2_vi0XzQ_tzH5esLeFDl236VqhHRTIRTKhPTtRbQmXXy1k-70AU1FJewVrQddxbzMXJLFclStIdG_vW1dWdqhh-hQ'

        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_def_response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_response.status_code, 201)

        self.task_def = task_def_response.data
        self.task_def_name = self.task_def['name']

    @patch('django.utils.timezone.now')
    def test_queueing(self, mocked_now):
        test_datetime = datetime.utcnow().isoformat() + 'Z'
        mocked_now.return_value = test_datetime

        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), task_keys)
        self.assertEqual(response.data['task_def']['name'], self.task_def_name)

        # test fields defaults
        self.assertEqual(response.data['status'], 'queued')
        self.assertEqual(response.data['priority'], 3)
        self.assertEqual(response.data['run_at'], test_datetime)

    def test_queueing_auth(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()

        response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_queue_with_unique(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), task_keys)

        self.assertEqual(response.data['unique'], 'classifer-2343')

    def test_queue_with_unique_conflict(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response1 = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(list(response1.data.keys()), task_keys)

        self.assertEqual(response1.data['unique'], 'classifer-2343')

        response2 = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.data['detail'], 'Task `unique` field conflict')

    def test_update_task(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(create_response.status_code, 201)

        update = create_response.data
        update['priority'] = 2

        update_response = client.put('/tasks/' + str(update['id']), update, format='json')

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(list(update_response.data.keys()), task_keys)
        self.assertEqual(update_response.data['priority'], 2)

    def test_update_task_auth(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(create_response.status_code, 201)

        client = APIClient() # clear token

        update = create_response.data
        update['priority'] = 2

        update_response = client.put('/tasks/' + str(update['id']), update, format='json')

        self.assertEqual(update_response.status_code, 401)
        self.assertEqual(update_response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_list_tasks(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_1_repsonse = client.post('/tasks', task_post_data, format='json')
        task_2_response = client.post('/tasks', task_post_data, format='json')

        client = APIClient() # clear token

        list_response = client.get('/tasks')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), task_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), task_keys)

    def test_get_task(self):
        task_post_data = {
            'task_def': {
                'name': self.task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_create_response = client.post('/tasks/', task_post_data, format='json')

        self.assertEqual(task_create_response.status_code, 201)

        client = APIClient() # clear token

        task_response = client.get('/tasks/' + str(task_create_response.data['id']))

        self.assertEqual(task_response.status_code, 200)
        self.assertEqual(list(task_response.data.keys()), task_keys)

    def test_create_nonexistent_task_def(self):
        task_def_name = 'nonexistent-task-def'
        task_post_data = {
            'task_def': {
                'name': task_def_name
            },
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_create_response = client.post('/tasks/', task_post_data, format='json')

        self.assertEqual(task_create_response.status_code, 201)
        self.assertEqual(task_create_response.data['task_def']['name'], task_def_name)
