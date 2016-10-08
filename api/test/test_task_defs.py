from rest_framework.test import APITestCase, APIClient

class TaskDefTests(APITestCase):
    task_def_keys = ['name',
                     'priority_levels',
                     'title',
                     'description',
                     'default_timeout',
                     'max_attempts',
                     'created_at',
                     'updated_at']

    def setUp(self):
        self.client = APIClient()

    def test_create_task_def(self):
        response = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), self.task_def_keys)
        self.assertEqual(response.data['name'], 'classifier-search')

        # test defaults
        self.assertEqual(response.data['title'], None)
        self.assertEqual(response.data['description'], None)
        self.assertEqual(response.data['max_attempts'], 1)
        self.assertEqual(response.data['priority_levels'], ['normal'])
        self.assertEqual(response.data['default_timeout'], 600)

    def test_update_task_def(self):
        create_response = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(create_response.status_code, 201)

        task_def = create_response.data
        task_def['title'] = 'Classifier Search'

        update_response = self.client.put('/task-defs/' + task_def['name'], task_def, format='json')

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['title'], 'Classifier Search')
        self.assertEqual(list(update_response.data.keys()), self.task_def_keys)

    def test_list_task_defs(self):
        task_def_1_repsonse = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')
        task_def_2_response = self.client.post('/task-defs', {'name': 'cleanup-workers'}, format='json')

        list_response = self.client.get('/task-defs')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.task_def_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.task_def_keys)

    def test_get_task_def(self):
        task_def_create_response = self.client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_create_response.status_code, 201)

        task_def_response = self.client.get('/task-defs/' + task_def_create_response.data['name'])

        self.assertEqual(task_def_response.status_code, 200)
        self.assertEqual(list(task_def_response.data.keys()), self.task_def_keys)
