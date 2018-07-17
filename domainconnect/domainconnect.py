import json

from six.moves import urllib

from dns.exception import Timeout
from dns.resolver import Resolver, NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers

from publicsuffix import PublicSuffixList
import webbrowser

from .network import get_json, get_http, http_request_json, NetworkContext

resolver = Resolver()
# TODO: support for custom nameservers needed
# if 'DNS_NAMESERVERS' in app.config:
#    resolver.nameservers = app.config['DNS_NAMESERVERS'].split(',')
psl = PublicSuffixList()


class DomainConnectConfig:
    domain = None
    domain_root = None
    host = None
    hosts = {}
    urlSyncUX = None
    urlAsyncUX = None
    urlAPI = None
    providerName = None
    uxSize = None

    def __init__(self, domain: str, domain_root: str, host: str, config: dict):
        self.domain = domain
        self.domain_root = domain_root
        self.host = host
        if 'urlSyncUX' in config:
            self.urlSyncUX = config['urlSyncUX']
        if 'urlAsyncUX' in config:
            self.urlAsyncUX = config['urlAsyncUX']
        if 'urlAPI' in config:
            self.urlAPI = config['urlAPI']
        if 'providerName' in config:
            self.providerName = config['providerName']
        if 'width' in config and 'height' in config:
            self.uxSize = (config['width'], config['height'])


class DomainConnectAsyncContext:
    config: DomainConnectConfig = None
    providerId: str = None
    serviceId: str = None
    client_secret: str = None
    asyncConsentUrl: str = None
    code: str = None
    params: dict = None
    return_url: str = None
    access_token: str = None
    refresh_token: str = None
    access_token_expires_in: int = None

    def __init__(self, config: DomainConnectConfig, provider_id: str, service_id: str, return_url: str, params: dict):
        self.config = config
        self.providerId = provider_id
        self.serviceId = service_id
        self.return_url = return_url
        self.params = params
        self.client_secret = ''


class DomainConnect:
    _networkContext = NetworkContext()

    def __init__(self, networkcontext=NetworkContext()):
        self._networkContext = networkcontext

    @staticmethod
    def identify_domain_root(domain):
        return psl.get_public_suffix(domain)

    @staticmethod
    def identify_domain_connect_api(domain_root):
        # noinspection PyBroadException
        try:
            dns = resolver.query('_domainconnect.{}'.format(domain_root), 'TXT')
            domain_connect_api = str(dns[0]).replace('"', '')
            print('Domain Connect API {} for {} found.'.format(domain_connect_api, domain_root))
            return domain_connect_api, None
        except Timeout:
            print('Timeout. Failed to find Domain Connect API for "{}"'.format(domain_root))
            return None, 'Timeout. Failed to find Domain Connect API for "{}"'.format(domain_root)
        except NXDOMAIN or YXDOMAIN:
            print('Failed to resolve "{}"'.format(domain_root))
            return None, 'Failed to resolve "{}"'.format(domain_root)
        except NoAnswer:
            print('No Domain Connect API found for "{}"'.format(domain_root))
            return None, 'No Domain Connect API found for "{}"'.format(domain_root)
        except NoNameservers:
            print('No nameservers avalaible for "{}"'.format(domain_root))
            return None, 'No nameservers avalaible for "{}"'.format(domain_root)
        except Exception:
            pass
        print('No Domain Connect API found for "{}"'.format(domain_root))
        return None, 'No Domain Connect API found for "{}"'.format(domain_root)

    @staticmethod
    def get_sync_url(config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlSyncUX' in config:
            return config['urlSyncUX'], None
        else:
            return None, 'No urlSyncUX in config'

    @staticmethod
    def get_async_url(config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlAsyncUX' in config:
            return config['urlAsyncUX'], None
        else:
            return None, 'No urlAsyncUX in config'

    @staticmethod
    def get_async_api_url(config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlAPI' in config:
            return config['urlAPI'], None
        else:
            return None, 'No urlAPI in config'

    @staticmethod
    def get_ux_size_url(config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: ((width, height), error text)
        """
        if 'width' in config and 'height' in config:
            return (config['width', 'height']), None
        else:
            return None, 'No width or height in config'

    def get_domain_config(self, domain: str) -> (DomainConnectConfig, str):
        """

        :param domain: domain name
        :return: (domain connect config, error text)
        """
        domain_root = self.identify_domain_root(domain)

        host = ''
        if len(domain_root) != len(domain):
            host = domain.replace('.' + domain_root, '')
        domain_connect_api, error = self.identify_domain_connect_api(domain_root)
        if error:
            return None, error
        else:
            ret, error2 = self._get_domain_config_for_root(domain_root, domain_connect_api)
            if error2:
                return None, error2
            else:
                return DomainConnectConfig(domain, domain_root, host, ret), None

    def _get_domain_config_for_root(self, domain_root: str, domain_connect_api: str) -> (dict, str):
        """

        :param domain_root: domain name for zone root
        :param domain_connect_api: URL of domain connect API of the vendor
        :return: (domain connect config, error text)
        """
        url = 'https://{}/v2/{}/settings'.format(domain_connect_api, domain_root)
        try:
            response = get_json(self._networkContext, url)
            print('Domain Connect config for {} over {}: {}'.format(domain_root, domain_connect_api,
                                                                    response))
            return response, None
        except Exception as e:
            print("Exception when getting config:{}".format(e))
        print('No Domain Connect config found for {}.'.format(domain_root))
        return None, 'No Domain Connect config found for {}.'.format(domain_root)

    def check_template_supported(self, config: DomainConnectConfig, provider_id: str, service_id: str) -> (dict, str):
        """

        :param config: domain connect config
        :param provider_id: provider_id to check
        :param service_id: service_id to check
        :return: (template supported, error)
        """
        url = '{}/v2/domainTemplates/providers/{}/services/{}' \
            .format(config.urlAPI, provider_id, service_id)

        try:
            response = get_http(self._networkContext, url)
            print('Template for serviceId: {} from {}: {}'.format(service_id, provider_id,
                                                                  response))
            return response, None
        except Exception as e:
            print("Exception when getting config:{}".format(e))
        print('No template for serviceId: {} from {}'.format(service_id, provider_id))
        return None, 'No template for serviceId: {} from {}'.format(service_id, provider_id)

    def get_domain_connect_template_sync_url(self, domain, provider_id, service_id, redirect_uri=None, params=None,
                                             state=None):
        # TODO: support for groupIds
        # TODO: support for signatures
        # TODO: support for provider_name (for shared templates)

        if params is None:
            params = {}

        config, error = self.get_domain_config(domain)

        if error is None:
            template, error_templ = self.check_template_supported(config, provider_id, service_id)

            if error_templ is not None:
                return None, error_templ

            if config.urlSyncUX is None:
                return None, "No sync URL in config"

            sync_url_format = '{}/v2/domainTemplates/providers/{}/services/{}/' \
                              'apply?domain={}&host={}&{}'

            if redirect_uri is not None:
                params["redirect_uri"] = redirect_uri
            if state is not None:
                params["state"] = state

            return sync_url_format.format(config.urlSyncUX, provider_id, service_id, config.domain_root, config.host,
                                          urllib.parse.urlencode(params)), None
        else:
            return None, error

    def get_domain_connect_template_async_url(self, domain, provider_id, service_id, redirect_uri, params=None,
                                              state=None, service_id_in_path=False) -> (DomainConnectAsyncContext, str):

        if params is None:
            params = {}
        config, error = self.get_domain_config(domain)

        if error is None:
            template, error_templ = self.check_template_supported(config, provider_id, service_id)

            if error_templ is not None:
                return None, error_templ

            if config.urlAsyncUX is None:
                return None, "No asynch UX URL in config"

            if service_id_in_path:
                async_url_format = '{0}/v2/domainTemplates/providers/{1}/services/{2}' \
                                   '?client_id={1}&scope={2}&domain={3}&host={4}&{5}'
            else:
                async_url_format = '{0}/v2/domainTemplates/providers/{1}' \
                                   '?client_id={1}&scope={2}&domain={3}&host={4}&{5}'

            if redirect_uri is not None:
                params["redirect_uri"] = redirect_uri
            if state is not None:
                params["state"] = state

            ret = DomainConnectAsyncContext(config, provider_id, service_id, redirect_uri, params)
            ret.asyncConsentUrl = async_url_format.format(config.urlAsyncUX, provider_id, service_id,
                                                          config.domain_root, config.host,
                                                          urllib.parse.urlencode(params))
            return ret, None
        else:
            return None, error

    def open_domain_connect_template_asynclink(self, domain, provider_id, service_id, redirect_uri, params=None,
                                               state=None, service_id_in_path=False):
        if params is None:
            params = {}
        async_context, error = self.get_domain_connect_template_async_url(domain, provider_id, service_id, redirect_uri,
                                                                          params, state, service_id_in_path)
        if error:
            return None, "Error when getting starting URL: {}".format(error)

        try:
            webbrowser.open_new_tab(async_context.asyncConsentUrl)
            return async_context, None
        except webbrowser.Error as err:
            return None, "Error opening browser window: {}".format(err)

    def get_async_token(self, context: DomainConnectAsyncContext) -> (DomainConnectAsyncContext, str):
        params = {'code': context.code, 'redirect_uri': context.return_url, 'grant_type': 'authorization_code'}

        # FIXME: context.config.urlAPI shall not be used here, as it may cause client_id/client_secret leakage by a malicious user
        url_get_access_token = '{}/v2/oauth/access_token?{}'.format(context.config.urlAPI,
                                                                    urllib.parse.urlencode(params))
        try:
            data = http_request_json(self._networkContext,
                                     method='POST',
                                     content_type='application/json',
                                     body=json.dumps({
                                         'client_id': context.providerId,
                                         'client_secret': context.client_secret,
                                     }),
                                     url=url_get_access_token
                                     )
        except Exception as ex:
            print('Cannot get async token: {}'.format(ex))
            return None, 'Cannot get async token: {}'.format(ex)

        if 'access_token' not in data \
                or 'expires_in' not in data \
                or 'token_type' not in data \
                or data['token_type'].lower() != 'bearer':
            print('Token not complete: {}'.format(data))
            return None, 'Token not complete: {}'.format(data)

        context.access_token = data['access_token']
        context.access_token_expires_in = data['expires_in']

        if 'refresh_token' in data:
            context.refresh_token = data['refresh_token']

        return context, None

    def apply_domain_connect_template_async(self, context: DomainConnectAsyncContext, host: str = None, service_id=None,
                                            params=None, force=False):
        # TODO: support for groupIds
        if params is None:
            params = {}
        if host is None:
            host = context.config.host
        if service_id is None:
            service_id = context.serviceId

        async_url_format = '{}/v2/domainTemplates/providers/{}/services/{}/' \
                           'apply?domain={}&host={}&{}'

        if force:
            params['force'] = 'true'

        url = async_url_format.format(context.config.urlAPI, context.providerId, service_id, context.config.domain_root,
                                      host, urllib.parse.urlencode(params))

        try:
            http_request_json(self._networkContext, 'POST', url, bearer=context.access_token)
            return "Success", None
        except Exception as e:
            return None, 'Error on apply: {}'.format(e)

    # TODO: implement revert
