import time
import unittest

from freezegun import freeze_time

import server


class BasicTests(unittest.TestCase):

    def setUp(self):
        server.application.config['TESTING'] = True
        server.application.config['TOKEN'] = 'token'
        server.application.config['DEBUG'] = False

        self.client = server.application.test_client()

    def test_mother_does_not_trust(self):
        response = self.client.get('/api/v1/status/child')
        self.assertEqual(response.status_code, 403)

    def test_mother_cares_for_child(self):
        response = self.client.post('/api/v1/nurture/child?token=token')
        self.assertEqual(response.status_code, 204)

    @freeze_time('2020-05-08 16:00')
    def test_mother_get_child_status(self):
        response = self.client.post('/api/v1/nurture/child2?token=token')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/v1/status/child2?token=token&format=json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            'last_cared': '2020-05-08T16:00:00+00:00',
            'name': 'child2',
            'status': 'ok'
        })

    def test_mother_get_child_status_when_bad(self):
        response = self.client.post('/api/v1/nurture/child3?token=token')
        self.assertEqual(response.status_code, 204)
        time.sleep(2)

        response = self.client.get('/api/v1/status/child3?token=token&format=json&timeout=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'critical')

    @freeze_time('2020-05-08 16:17')
    def test_mother_gets_visual_indication(self):
        response = self.client.post('/api/v1/nurture/child4?token=token')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/v1/status/child4?token=token&format=pixel&timeout=1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://via.placeholder.com/360x120/00ff00?text=May%2008%2018:17')

if __name__ == "__main__":
    unittest.main()
