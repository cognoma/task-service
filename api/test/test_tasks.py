from datetime import datetime, timezone
from unittest.mock import patch

from rest_framework.test import APITestCase, APIClient

class TaskTests(APITestCase):
    task_keys = ['id',
                 'task_def',
                 'status',
                 'worker_id',
                 'received_at',
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

    def setUp(self):
        self.client = APIClient()

        task_def_response = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_response.status_code, 201)

        self.task_def = task_def_response.data
        self.task_def_name = self.task_def['name']

    @patch('django.utils.timezone.now')
    def test_queueing(self, mocked_now):
        test_datetime = datetime.utcnow().isoformat() + 'Z'

        mocked_now.return_value = test_datetime

        task_post_data = {
            'task_def': self.task_def_name,
            'data': {
                'foo': 'bar'
            }
        }

        response = self.client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), self.task_keys)
        self.assertEqual(response.data['task_def'], self.task_def_name)

        ## test fields defaults
        self.assertEqual(response.data['status'], 'queued')
        self.assertEqual(response.data['priority'], 'normal')
        self.assertEqual(response.data['run_at'], test_datetime)

    def test_queue_with_unique(self):
        task_post_data = {
            'task_def': self.task_def_name,
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        response = self.client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), self.task_keys)

        self.assertEqual(response.data['unique'], 'classifer-2343')

    def test_queue_with_unique_conflict(self):
        task_post_data = {
            'task_def': self.task_def_name,
            'unique': 'classifer-2343',
            'data': {
                'foo': 'bar'
            }
        }

        response1 = self.client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(list(response1.data.keys()), self.task_keys)

        self.assertEqual(response1.data['unique'], 'classifer-2343')

        response2 = self.client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.data['detail'], 'Task `unique` field conflict')
