import unittest
from hermes.automate import *


class FakeSource(Source):

    def titre(self):
        return 'FakeSource'

    def corps(self):
        return ''


class TestAction(unittest.TestCase):

    def test_http_ok(self):
        action = RequeteHttpActionNoeud(
            "Requête sur httpbin",
            "https://httpbin.org/post",
            "POST",
            {
                'username': 'abc',
                'password': 'xyz'
            },
            None,
            None,
            200
        )

        self.assertTrue(
            action.je_realise(FakeSource('', ''))
        )

        self.assertIn(
            'form',
            action.payload
        )

        self.assertEqual(
            {
                'username': 'abc',
                'password': 'xyz'
            },
            action.payload['form']
        )

    def test_http_ko(self):
        action = RequeteHttpActionNoeud(
            "Requête sur httpbin",
            "https://httpbin.org/post",
            "POST",
            {
                'username': 'abc',
                'password': 'xyz'
            },
            None,
            None,
            201
        )

        self.assertFalse(
            action.je_realise(FakeSource('', ''))
        )


if __name__ == '__main__':
    unittest.main()
