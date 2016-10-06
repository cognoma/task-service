from rest_framework.test import APITestCase, APIClient

class TaskTests(APITestCase):
    task_keys = ['id',
                 'task_def',
                 'status',
                 'worker_id',
                 'received_at',
                 'priority',
                 'unique',
                 'started_at',
                 'completed_at',
                 'failed_at',
                 'data',
                 'attempts',
                 'created_at',
                 'updated_at']

    def setUp(self):
        self.client = APIClient()
