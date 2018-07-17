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
    providerId = None
    providerName = None
    providerDisplayName = None
    uxSize = None
    urlControlPanel = None

    def __init__(self, domain, domain_root, host, config):
        """Creates config object from /settings output of DNS provider

        :param domain: str
        :param domain_root: str
        :param host: str
        :param config: dict
        """
        self.domain = domain
        self.domain_root = domain_root
        self.host = host
        if 'urlSyncUX' in config:
            self.urlSyncUX = config['urlSyncUX']
        if 'urlAsyncUX' in config:
            self.urlAsyncUX = config['urlAsyncUX']
        if 'urlAPI' in config:
            self.urlAPI = config['urlAPI']
        if 'providerId' in config:
            self.providerId = config['providerId']
        if 'providerName' in config:
            self.providerName = config['providerName']
        if 'providerDisplayName' in config:
            self.providerDisplayName = config['providerDisplayName']
        if 'width' in config and 'height' in config:
            self.uxSize = (config['width'], config['height'])
        if 'urlControlPanel' in config:
            self.urlControlPanel = config['urlControlPanel']


class DomainConnectAsyncContext:
    config = None
    """ :type: DomainConnectConfig """
    providerId = None
    """ :type: str """
    serviceId = None
    """ :type: str """
    client_secret = None
    """ :type: str """
    asyncConsentUrl = None
    """ :type: str """
    code = None
    """ :type: str """
    params = None
    """ :type: dict """
    return_url = None
    """ :type: str """
    access_token = None
    """ :type: str """
    refresh_token = None
    """ :type: str """
    access_token_expires_in = None
    """ :type: int """

    def __init__(self, config, provider_id, service_id, return_url, params):
        """Initiates the object

        :param config: DomainConnectConfig
            Config. See: DomainConnect.get_domain_config
        :param provider_id: str
        :param service_id: str
        :param return_url: str
            Return URL of the request
        :param params: dict
        """
        self.config = config
        self.providerId = provider_id
        self.serviceId = service_id
        self.return_url = return_url
        self.params = params
        self.client_secret = ''


class DomainConnectAsyncCredentials:
    client_id = None
    """ :type: str """
    client_secret = None
    """ :type: str """
    api_url = None
    """ :type: str """

    def __init__(self, client_id, client_secret, api_url):
        """Initializes the object

        :param client_id: str
        :param client_secret: str
        :param api_url: str
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url


class DomainConnect:
    _networkContext = NetworkContext()

    def __init__(self, networkcontext=NetworkContext()):
        self._networkContext = networkcontext

    @staticmethod
    def identify_domain_root(domain):
        return psl.get_public_suffix(domain)

    @staticmethod
    def _identify_domain_connect_api(domain_root):
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

    def get_domain_config(self, domain):
        """Makes a discovery of domain name and resolves configuration of DNS provider

        :param domain: str
            domain name
        :return: (DomainConnectConfig, str)
            (domain connect config, error text)
        """
        domain_root = self.identify_domain_root(domain)

        host = ''
        if len(domain_root) != len(domain):
            host = domain.replace('.' + domain_root, '')
        domain_connect_api, error = self._identify_domain_connect_api(domain_root)
        if error:
            return None, error
        else:
            ret, error2 = self._get_domain_config_for_root(domain_root, domain_connect_api)
            if error2:
                return None, error2
            else:
                return DomainConnectConfig(domain, domain_root, host, ret), None

    def _get_domain_config_for_root(self, domain_root, domain_connect_api):
        """

        :param domain_root: str
            domain name for zone root
        :param domain_connect_api: str
            URL of domain connect API of the vendor
        :return: (dict, str)
            (domain connect config, error text)
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

    def check_template_supported(self, config, provider_id, service_id):
        """

        :param config: DomainConnectConfig
            domain connect config
        :param provider_id: str
            provider_id to check
        :param service_id: str
            service_id to check
        :return: (dict, str)
            (template supported, error)
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
        """Makes full Domain Connect discovery of a domain and returns full url to request sync consent.

        :param domain: str
        :param provider_id: str
        :param service_id: str
        :param redirect_uri: str
        :param params: dict
        :param state: str
        :return: (str, str)
            first field is an url which shall be used to redirect the browser to
            second field is an indication of error
        """
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
                                          urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0]))), None
        else:
            return None, error

    def get_domain_connect_template_async_context(self, domain, provider_id, service_id, redirect_uri, params=None,
                                                  state=None, service_id_in_path=False):
        """Makes full Domain Connect discovery of a domain and returns full context to request async consent.

        :param domain: str
        :param provider_id: str
        :param service_id: str
        :param redirect_uri: str
        :param params: dict
        :param state: str
        :param service_id_in_path: bool
        :return: (DomainConnectAsyncContext, str)
            asyncConsentUrl field of returned context shall be used to redirect the browser to
            second field is an indication of error
        """
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
                                                          urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0])))
            return ret, None
        else:
            return None, error

    def open_domain_connect_template_asynclink(self, domain, provider_id, service_id, redirect_uri, params=None,
                                               state=None, service_id_in_path=False):
        if params is None:
            params = {}
        async_context, error = self.get_domain_connect_template_async_context(
            domain, provider_id, service_id, redirect_uri, params, state, service_id_in_path)
        if error:
            return None, "Error when getting starting URL: {}".format(error)

        try:
            print ('Please open URL: {}'.format(async_context.asyncConsentUrl))
            webbrowser.open_new_tab(async_context.asyncConsentUrl)
            return async_context, None
        except webbrowser.Error as err:
            return None, "Error opening browser window: {}".format(err)

    def get_async_token(self, context, credentials):
        """Gets access_token in async process

        :param context: DomainConnectAsyncContext
        :param credentials: DomainConnectAsyncCredentials
        :return: (DomainConnectAsyncContext, str)
            (context enriched with access_token and refresh_token if existing, error)
        """
        params = {'code': context.code, 'redirect_uri': context.return_url, 'grant_type': 'authorization_code'}

        # FIXME: context.config.urlAPI shall not be used here, as it may cause client_id/client_secret leakage by
        # a malicious user
        url_get_access_token = '{}/v2/oauth/access_token?{}'.format(context.config.urlAPI,
                                                                    urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0])))
        try:
            # this has to be checked to avoid secret leakage by spoofed "settings" end-point
            if credentials.api_url != context.config.urlAPI:
                raise Exception("URL API for provider does not match registered one with credentials")
            data = http_request_json(self._networkContext,
                                     method='POST',
                                     content_type='application/json',
                                     body=json.dumps({
                                         'client_id': credentials.client_id,
                                         'client_secret': credentials.client_secret,
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

    def apply_domain_connect_template_async(self, context, host=None, service_id=None,
                                            params=None, force=False):
        """

        :param context: DomainConnectAsyncContext
        :param host: str
        :param service_id:
        :param params:
        :param force:
        :return: (str, str)
            If success it's ("Success", None), otherwise (None, error)
        """
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
                                      host, urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0])))

        try:
            http_request_json(self._networkContext, 'POST', url, bearer=context.access_token)
            return "Success", None
        except Exception as e:
            return None, 'Error on apply: {}'.format(e)

    # TODO: implement revert
