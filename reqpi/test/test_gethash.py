from __future__ import print_function
from unittest import TestCase
import json

from reqpi import gethash


class MockSession:

    def __init__(self, status=200):
        self.status = status

    def post(self, *a, **ka):
        response = MockResponse(self.status)
        return response


class MockResponse:

    def __init__(self, status):
        self.status_code = status
        self.text = json.dumps({'url': 'the_url'})


class TestHash(TestCase):

    def test_required_args(self):
        with self.assertRaises(SystemExit):
            gethash.PARSER.parse_args([])

    def test_main(self):
        with open('reqs.txt', 'w') as f:
            f.write('test==1.0\n')
        gethash.main(['gethash', 'reqs.txt'], MockSession)

    def test_empty_requirements_disallowed(self):
        with self.assertRaises(Exception):
            gethash.main(['gethash', '/does_not_exist'])

    def test_get_server_url_returns_url(self):
        session = MockSession()
        url = gethash.get_package_server_url(session,
                                             'dummy_server',
                                             ['a==1', 'b==2'])
        self.assertEqual('the_url', url)

    def test_bad_return_status_throws(self):
        session = MockSession(503)
        with self.assertRaises(Exception):
            gethash.get_package_server_url(session,
                                           'dummy_server',
                                           ['a==1', 'b==2'])
