# coding: utf-8

from argparse import ArgumentParser
import itertools
import re
import socket
import sys


class Url(object):

    _patterns = {
        'scheme': r"(?P<scheme>http)",
        'host': r"(?P<host>[a-zA-Z0-9$\- .+!*'(),%]+|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)",
        'port': r"(?P<port>[0-9]+)",
        'path': r"(?P<path>[a-zA-Z0-9$/\-.+ !*'(),%;&=]+)",
        'query': r"(?P<query>[a-zA-Z0-9$\- .+!*'(),%;?&=]+)",
    }

    URL_PATTERN = re.compile(r"{scheme}?(://)?{host}:?{port}?{path}?\??{query}?".format(**_patterns))

    @classmethod
    def _parse(cls, url: str) -> str:
        matched = cls.URL_PATTERN.match(url)
        if matched is not None:
            return dict(
                scheme=matched.group('scheme'),
                host=matched.group('host'),
                port=matched.group('port'),
                path=matched.group('path'),
                query=matched.group('query'),
            )
        raise ValueError('url {url} does not match url specifications'.format(url=url))

    def __init__(self, url):
        self._url = url
        self._parsed = self._parse(url)

    @property
    def scheme(self) -> str:
        return self._parsed['scheme'] or 'http'

    @property
    def host(self) -> str:
        return self._parsed['host']

    @property
    def port(self) -> str:
        return self._parsed['port'] or '80'

    @property
    def path(self) -> str:
        return self._parsed['path'] or '/'

    @property
    def query(self) -> str:
        return self._parsed['query'] or ''


class Response(object):

    def __init__(self, data: bytes):
        self._data = data
        self._decoded = data.decode('utf-8')

    def __str__(self):
        return self._decoded

    @property
    def status(self):
        return self._decoded.splitlines()[0]

    @property
    def header(self):
        return '\n'.join(list(itertools.takewhile(lambda x: bool(x), self._decoded.splitlines()))[1:])

    @property
    def body(self):
        return '\n'.join(list(itertools.dropwhile(lambda x: bool(x), self._decoded.splitlines()))[1:])


class Pyurl(object):

    def request(self, url: Url, method: str = 'GET') -> Response:
        addresses = socket.getaddrinfo(
            host=url.host, port=url.port, family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM, proto=0, flags=socket.AI_PASSIVE)
        s = None
        for af, socktype, proto, canonname, sa in addresses:
            try:
                s = socket.socket(af, socktype, proto)
            except OSError:
                continue
            try:
                s.connect(sa)
            except OSError:
                s = None
                continue
            break
        if s is None:
            print('could not open socket')
            sys.exit(1)
        with s:
            headers = ['Host: {host}'.format(host=url.host)]
            if url.query:
                path = '{path}?{query}'.format(path=url.path, query=url.query)
            else:
                path = url.path
            request = '{method} {path} HTTP/1.1\r\n'.format(method='GET', path=path).encode('utf-8') + \
                '{headers}\r\n\r\n'.format(headers='\r\n'.join(headers)).encode('utf-8')
            s.sendall(request)

            data = s.recv(4096)

            return Response(data)


def main():
    kwargs = from_commandline()
    pyurl = Pyurl()
    response = pyurl.request(Url(kwargs.url))

    if kwargs.status:
        print(response.status)
    if kwargs.header:
        print(response.header)
    if kwargs.body:
        print(response.body)


def from_commandline():
    parser = ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-s', '--status', default=False, action='store_true', help='output status line')
    parser.add_argument('-H', '--header', default=False, action='store_true', help='output header lines')
    parser.add_argument('-B', '--body', default=True, action='store_true', help='output header lines')

    return parser.parse_args()


if __name__ == '__main__':
    main()
