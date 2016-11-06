from datetime import datetime, timedelta
from unittest.mock import patch

from rest_framework.test import APITestCase, APIClient

from api.test.test_tasks import task_keys

class TaskQueueTests(APITestCase):
    @patch('django.utils.timezone.now')
    def setUp(self, mocked_now):
        # now needs to be padded to account for API and db clocks not in perfect sync
        test_datetime = (datetime.utcnow() - timedelta(0,3)).isoformat() + 'Z'

        mocked_now.return_value = test_datetime

        client = APIClient()

        self.token = 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXJ2aWNlIjoiY29yZSJ9.HHlbWMjo-Y__DGV0DAiCY7u85FuNtY8wpovcZ9ga-oCsLdM2H5iVSz1vKiWK8zxl7dSYltbnyTNMxXO2cDS81hr4ohycr7YYg5CaE5sA5id73ab5T145XEdF5X_HXoeczctGq7X3x9QYSn7O1fWJbPWcIrOCs6T2DrySsYgjgdAAnWnKedy_dYWJ0YtHY1bXH3Y7T126QqVlQ9ylHk6hmFMCtxMPbuAX4YBJsxwjWpMDpe13xbaU0Uqo5N47a2_vi0XzQ_tzH5esLeFDl236VqhHRTIRTKhPTtRbQmXXy1k-70AU1FJewVrQddxbzMXJLFclStIdG_vW1dWdqhh-hQ'

        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_def_response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_response.status_code, 201)

        self.task_def = task_def_response.data
        self.task_def_name = self.task_def['name']

        self.task_number = 0

        for x in range(0,10):
            self.schedule_task(client)

    def schedule_task(self, client, run_at=None, priority=None):
        self.task_number += 1
        task_post_data = {
            'task_def': self.task_def_name,
            'unique': 'classifier-' + str(self.task_number),
            'data': {
                'foo': 'bar'
            }
        }

        if run_at != None:
            task_post_data['run_at'] = run_at

        if priority != None:
            task_post_data['priority'] = priority

        response = client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)

        return response.data

    def test_pull_from_queue(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(list(response.data[0].keys()), task_keys)

    def test_pull_from_queue_auth(self):
        client = APIClient()

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_pull_from_queue_with_limit(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo&limit=10')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 10)

        for task in response.data:
            self.assertEqual(list(task.keys()), task_keys)

    @patch('django.utils.timezone.now')
    def test_pull_from_queue_order(self, mocked_now):
        # now needs to be padded to account for API and db clocks not in perfect sync
        test_datetime = (datetime.utcnow() - timedelta(0,3)).isoformat() + 'Z'

        mocked_now.return_value = test_datetime

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        minus_10_min = (datetime.utcnow() - timedelta(0,600)).isoformat() + 'Z'

        ## purposely not ordered by the actual expected by pull
        task1 = self.schedule_task(client, run_at=minus_10_min)
        task2 = self.schedule_task(client, priority='high')
        task3 = self.schedule_task(client, priority='low')
        task4 = self.schedule_task(client, run_at=minus_10_min, priority='high')

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')
        self.assertEqual(task4['id'], response.data[0]['id'])

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')
        self.assertEqual(task2['id'], response.data[0]['id'])

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')
        self.assertEqual(task1['id'], response.data[0]['id'])

        ## All the 'normal' priority tasks from setUp() should be here
        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo&limit=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

        response = client.get('/tasks/queue?tasks=' + self.task_def_name + '&worker_id=foo')
        self.assertEqual(task3['id'], response.data[0]['id'])
