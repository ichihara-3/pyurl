# coding: utf-8

from pyurl import Url


class TestUrl(object):

    def test_url(self):
        url = Url('http://www.example.com:8000/hello/world?query=hogehoge')
        assert url.scheme == 'http'
        assert url.host == 'www.example.com'
        assert url.port == '8000'
        assert url.path == '/hello/world'
        assert url.query == 'query=hogehoge'

        url = Url('www.example.com')
        assert url.scheme == 'http'
        assert url.host == 'www.example.com'
        assert url.port == '80'
        assert url.path == '/'
        assert url.query == ''

    def test_url_parse(self):
        parsed = Url._parse(
            'http://www.example.com:8080/hello/world?query=hogehoge')
        expected = {
            'scheme': 'http',
            'host': 'www.example.com',
            'port': '8080',
            'path': '/hello/world',
            'query': 'query=hogehoge',
        }
        assert parsed == expected

        parsed = Url._parse('http://www.example.com')
        expected = {
            'scheme': 'http',
            'host': 'www.example.com',
            'port': None,
            'path': None,
            'query': None,
        }
        assert parsed == expected

        parsed = Url._parse('http://192.168.0.1:8080/test/path?a=b')
        expected = {
            'scheme': 'http',
            'host': '192.168.0.1',
            'port': '8080',
            'path': '/test/path',
            'query': 'a=b',
        }
        assert parsed == expected
