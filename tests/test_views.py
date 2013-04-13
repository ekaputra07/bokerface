from base import TestBase


class TestViews(TestBase):

    def test_homepage(self):
        
        # Make sure homepage accessible
        resp = self.client.get('/')
        self.assertEqual(resp.status_int, 200)
