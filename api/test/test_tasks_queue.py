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

        self.client = APIClient()

        task_def_response = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_response.status_code, 201)

        self.task_def = task_def_response.data
        self.task_def_name = self.task_def['name']

        self.task_number = 0

        for x in range(0,11):
            self.schedule_task()

    def schedule_task(self):
        self.task_number += 1
        task_post_data = {
            'task_def': self.task_def_name,
            'unique': 'classifier-' + str(self.task_number),
            'data': {
                'foo': 'bar'
            }
        }

        response = self.client.post('/tasks', task_post_data, format='json')

        self.assertEqual(response.status_code, 201)

    def test_pull_from_queue(self):
        response = self.client.get('/tasks/queue?tasks=' + self.task_def_name)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(list(response.data[0].keys()), task_keys)

    def test_pull_from_queue_with_limit(self):
        response = self.client.get('/tasks/queue?tasks=' + self.task_def_name + '&limit=10')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 10)

        for task in response.data:
            self.assertEqual(list(task.keys()), task_keys)
