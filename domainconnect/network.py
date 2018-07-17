import base64
import json
import re
import ssl

from six.moves import http_client as client


class NetworkContext:
    proxyHost = None
    proxyPort = None

    def __init__(self, proxy_host = None, proxy_port = None):
        self.proxyPort = proxy_port
        self.proxyHost = proxy_host


def http_request_json(context, method, url, body=None, basic_auth=None, bearer=None,
                      content_type=None, cache_control=None):
    """

    :param context: NetworkContext
    :param method: str
    :param url: str
    :param body: str
    :param basic_auth: str
    :param bearer: str
    :param content_type: str
    :param cache_control: str
    :return:
    """
    return json.loads(http_request(context=context,
                                   method=method,
                                   url=url,
                                   body=body,
                                   basic_auth=basic_auth,
                                   bearer=bearer,
                                   content_type=content_type,
                                   cache_control=cache_control,
                                   accepts='application/json'))


def http_request(context, method, url, body=None, basic_auth=None, bearer=None, content_type=None,
                 accepts=None, cache_control=None):
    """

    :param context: NetworkContext
    :param method: str
    :param url: str
    :param body: str
    :param basic_auth: str
    :param bearer: str
    :param content_type: str
    :param accepts: str
    :param cache_control: str
    :return:
    """
    connection = None
    url_parts = re.match('(?i)(https?)://([^:/]+(?::\d+)?)(/.*)', url)
    if url_parts is None:
        raise Exception('Given issuer is not a valid URL')
    protocol = url_parts.group(1).lower()
    host = url_parts.group(2)
    path = url_parts.group(3)
    print('method = {} protocol = {}, host = {}, path = {}'.format(method, protocol, host, path))
    try:
        if protocol == 'http':
            if context.proxyHost is not None and context.proxyPort is not None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPConnection(context.proxyHost, context.proxyPort)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPConnection(host)
        else:
            # noinspection PyProtectedMember
            ssl_context = ssl._create_unverified_context()
            if context.proxyHost is not None and context.proxyPort is not None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPSConnection(context.proxyHost, context.proxyPort, context=ssl_context)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPSConnection(host, context=ssl_context)
        header = dict()
        if basic_auth is not None:
            user, password = basic_auth
            head = ':'.join([user, password]).encode()
            header['Authorization'] = ' '.join(['Basic', base64.b64encode(head).decode()])
        if bearer is not None:
            header['Authorization'] = ' '.join(['Bearer', bearer])
        if content_type is not None:
            header['Content-Type'] = content_type
        if accepts is not None:
            header['Accept'] = accepts
        if cache_control is not None:
            header['Cache-Control'] = cache_control
        connection.request(method, path, body, header)
        response = connection.getresponse()
        if response.status != 200:
            print('Failed to query {}: {}'.format(url, response.status))
            raise Exception('Failed to read from {}. HTTP code: {}'.format(url, response.status))
        ret = response.read().decode('utf-8')
    finally:
        if connection is not None:
            connection.close()
    return ret


def post_data(context, url, data, basic_auth=None, bearer=None):
    """

    :param context: NetworkContext
    :param url: str
    :param data: str
    :param basic_auth: str
    :param bearer: str
    :return:
    """
    response = http_request(context=context, method='POST', url=url, body=data, basic_auth=basic_auth,
                            bearer=bearer, content_type='application/x-www-form-urlencoded')
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to POST data to {}'.format(url))
    return response.read().decode('utf-8')


def post_json(context, url, content, basic_auth=None, bearer=None):
    """

    :param context: NetworkContext
    :param url: str
    :param content: str
    :param basic_auth: str
    :param bearer: str
    :return:
    """
    response = http_request(context=context, method='POST', url=url, body=json.dumps(content), basic_auth=basic_auth,
                            bearer=bearer, content_type='application/json')
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to POST json to {}'.format(url))
    return response.read().decode('utf-8')


def get_json(context, url):
    """

    :param context: NetworkContext
    :param url: str
    :return:
    """
    return json.loads(get_http(context, url))


def get_http(context, url):
    """

    :param context: NetworkContext
    :param url: str
    :return:
    """
    connection = None
    url_parts = re.match('(?i)(https?)://([^:/]+(?::\d+)?)(/.*)', url)
    if url_parts is None:
        raise Exception('Given issuer is not a valid URL')
    protocol = url_parts.group(1).lower()
    host = url_parts.group(2)
    path = url_parts.group(3)
    print('protocol = {}, host = {}, path = {}'.format(protocol, host, path))
    try:
        if protocol == 'http':
            if context.proxyHost is not None and context.proxyPort is not None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPConnection(context.proxyHost, context.proxyPort)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPConnection(host)
        else:
            # noinspection PyProtectedMember
            ssl_context = ssl._create_unverified_context()
            if context.proxyHost is not None and context.proxyPort is not None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPSConnection(context.proxyHost, context.proxyPort, context=ssl_context)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPSConnection(host, context=ssl_context)
        connection.request('GET', path)
        response = connection.getresponse()
        if response.status != 200:
            print('Failed to query {}: {}'.format(url, response.status))
            raise Exception('Failed to read from {}'.format(url))
        ret = response.read().decode('utf-8')
    finally:
        if connection is not None:
            connection.close()
    return ret


def get_json_auth(context, url, basic_auth=None, bearer=None):
    """

    :param context: NetworkContext
    :param url: str
    :param basic_auth: str
    :param bearer: str
    :return:
    """
    response = http_request(context=context, method='GET', url=url, basic_auth=basic_auth, bearer=bearer)
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to GET from {}'.format(url))
    return json.loads(response.read().decode('utf-8'))
