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
        self.token = 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXJ2aWNlIjoiY29yZSJ9.HHlbWMjo-Y__DGV0DAiCY7u85FuNtY8wpovcZ9ga-oCsLdM2H5iVSz1vKiWK8zxl7dSYltbnyTNMxXO2cDS81hr4ohycr7YYg5CaE5sA5id73ab5T145XEdF5X_HXoeczctGq7X3x9QYSn7O1fWJbPWcIrOCs6T2DrySsYgjgdAAnWnKedy_dYWJ0YtHY1bXH3Y7T126QqVlQ9ylHk6hmFMCtxMPbuAX4YBJsxwjWpMDpe13xbaU0Uqo5N47a2_vi0XzQ_tzH5esLeFDl236VqhHRTIRTKhPTtRbQmXXy1k-70AU1FJewVrQddxbzMXJLFclStIdG_vW1dWdqhh-hQ'

    def test_create_task_def(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), self.task_def_keys)
        self.assertEqual(response.data['name'], 'classifier-search')

        # test defaults
        self.assertEqual(response.data['title'], None)
        self.assertEqual(response.data['description'], None)
        self.assertEqual(response.data['max_attempts'], 1)
        self.assertEqual(response.data['priority_levels'], ['normal'])
        self.assertEqual(response.data['default_timeout'], 600)

    def test_create_task_def_auth(self):
        client = APIClient()

        response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_update_task_def(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(create_response.status_code, 201)

        task_def = create_response.data
        task_def['title'] = 'Classifier Search'

        update_response = client.put('/task-defs/' + task_def['name'], task_def, format='json')

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['title'], 'Classifier Search')
        self.assertEqual(list(update_response.data.keys()), self.task_def_keys)

    def test_update_task_def_auth(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(create_response.status_code, 201)

        client = APIClient() # clear token

        task_def = create_response.data
        task_def['title'] = 'Classifier Search'

        update_response = client.put('/task-defs/' + task_def['name'], task_def, format='json')

        self.assertEqual(update_response.status_code, 401)
        self.assertEqual(update_response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_list_task_defs(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_def_1_repsonse = client.post('/task-defs', {'name': 'classifier-search'}, format='json')
        task_def_2_response = client.post('/task-defs', {'name': 'cleanup-workers'}, format='json')

        client = APIClient() # clear token

        list_response = client.get('/task-defs')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.task_def_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.task_def_keys)

    def test_get_task_def(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        task_def_create_response = client.post('/task-defs', {'name': 'classifier-search'}, format='json')

        self.assertEqual(task_def_create_response.status_code, 201)

        client = APIClient() # clear token

        task_def_response = client.get('/task-defs/' + task_def_create_response.data['name'])

        self.assertEqual(task_def_response.status_code, 200)
        self.assertEqual(list(task_def_response.data.keys()), self.task_def_keys)
