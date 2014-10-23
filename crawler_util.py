import cgi
from html.parser import HTMLParser
import threading
import urllib.parse

__author__ = 'pahaz'


class UrlThreadSafeStore(object):
    def __init__(self):
        self._store = set()
        self._lock = threading.Lock()

    def check_and_add(self, obj):
        self._lock.acquire()
        has = obj in self._store
        self._store.add(obj)
        self._lock.release()
        return has


def save_binary_data_to_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)


class _HTMLURLFinder(HTMLParser):
    def __init__(self, output_list=None):
        HTMLParser.__init__(self)
        if output_list is None:
            self.output_list = []
        else:
            self.output_list = output_list

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.output_list.append(dict(attrs).get('href'))


def get_links(url, u_head, u_data):
    headers = dict(u_head)
    encoding = get_encoding_from_headers(headers)
    try:
        data = u_data.decode(encoding)
    except UnicodeDecodeError:
        print("UnicodeDecodeError: {0}".format(url))
        return []

    p = _HTMLURLFinder()
    p.feed(data)
    return [urllib.parse.urljoin(url, u) for u in p.output_list]


def get_encoding_from_headers(headers):
    """Returns encodings from given HTTP Header Dict.

    :param headers: dictionary to extract encoding from.
    """

    content_type = headers.get('content-type')

    if not content_type:
        return None

    content_type, params = cgi.parse_header(content_type)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'
