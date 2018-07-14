import base64
import json
import re
import ssl

from http import client

class NetworkContext:
    proxyHost = None
    proxyPort = None

    def __init__(self, proxyHost: str = None, proxyPort: str = None) -> object:
        self.proxyPort = proxyPort
        self.proxyHost = proxyHost

def http_request(method, url, body=None, basic_auth=None, bearer=None, content_type=None, cache_control=None):
    url_parts = re.match('(?i)(https?)://([^:/]+(?::\d+)?)(/.*)', url)
    if url_parts is None:
        raise Exception('Given issuer is not a valid URL')
    protocol = url_parts.group(1).lower()
    host = url_parts.group(2)
    path = url_parts.group(3)
    print('method = {} protocol = {}, host = {}, path = {}'.format(method, protocol, host, path))
    if protocol == 'http':
        if 'PROXY_HOST' in app.config and 'PROXY_PORT' in app.config:
            print('using proxy {}:{}'.format(app.config['PROXY_HOST'], app.config['PROXY_PORT']))
            connection = client.HTTPConnection(app.config['PROXY_HOST'], app.config['PROXY_PORT'])
            connection.set_tunnel(host)
        else:
            connection = client.HTTPConnection(host)
    else:
        if 'PROXY_HOST' in app.config and 'PROXY_PORT' in app.config:
            print('using proxy {}:{}'.format(app.config['PROXY_HOST'], app.config['PROXY_PORT']))
            connection = client.HTTPSConnection(app.config['PROXY_HOST'], app.config['PROXY_PORT'])
            connection.set_tunnel(host)
        else:
            connection = client.HTTPSConnection(host)
    header = dict()
    if basic_auth is not None:
        user, password = basic_auth
        head = ':'.join([user, password]).encode()
        header['Authorization'] = ' '.join(['Basic', base64.b64encode(head).decode()])
    if bearer is not None:
        header['Authorization'] = ' '.join(['Bearer', bearer])
    if content_type is not None:
        header['Content-Type'] = content_type
    if cache_control is not None:
        header['Cache-Control'] = cache_control
    connection.request(method, path, body, header)
    return connection.getresponse()


def post_data(url, data, basic_auth=None, bearer=None):
    response = http_request('POST', url, body=data, basic_auth=basic_auth,
                            bearer=bearer, content_type='application/x-www-form-urlencoded')
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to POST data to {}'.format(url))
    return response.read().decode('utf-8')


def post_json(url, content, basic_auth=None, bearer=None):
    response = http_request('POST', url, body=json.dumps(content), basic_auth=basic_auth,
                            bearer=bearer, content_type='application/json')
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to POST json to {}'.format(url))
    return response.read().decode('utf-8')


def get_json(context: NetworkContext, url):
    url_parts = re.match('(?i)(https?)://([^:/]+(?::\d+)?)(/.*)', url)
    if url_parts is None:
        raise BadRequest('Given issuer is not a valid URL')
    protocol = url_parts.group(1).lower()
    host = url_parts.group(2)
    path = url_parts.group(3)
    print('protocol = {}, host = {}, path = {}'.format(protocol, host, path))
    ret = ''
    try:
        if protocol == 'http':
            if context.proxyHost != None and context.proxyPort != None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPConnection(context.proxyHost, context.proxyPort)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPConnection(host)
        else:
            sslContext = ssl._create_unverified_context()
            if context.proxyHost != None and context.proxyPort != None:
                print('using proxy {}:{}'.format(context.proxyHost, context.proxyPort))
                connection = client.HTTPSConnection(context.proxyHost, context.proxyPort, context=sslContext)
                connection.set_tunnel(host)
            else:
                connection = client.HTTPSConnection(host, context=sslContext)
        connection.request('GET', path)
        response = connection.getresponse()
        if response.status != 200:
            print('Failed to query {}: {}'.format(url, response.status))
            raise Exception('Failed to read from {}'.format(url))
        ret = json.loads(response.read().decode('utf-8'))
    finally:
        if (connection is not None):
            connection.close()
    return ret


def get_json_auth(url, basic_auth=None, bearer=None):
    response = http_request('GET', url, basic_auth=basic_auth, bearer=bearer)
    if response.status != 200:
        print(response.getheaders())
        raise Exception('Failed to GET from {}'.format(url))
    return json.loads(response.read().decode('utf-8'))
