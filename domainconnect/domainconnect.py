from six.moves import urllib

from dns.exception import Timeout
from dns.resolver import Resolver, NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers

from publicsuffix import PublicSuffixList

from .network import get_json, NetworkContext

resolver = Resolver()
#if 'DNS_NAMESERVERS' in app.config:
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

    def __init__(self, domain:str, domain_root: str, host: str, config: dict):
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

class DomainConnect:
    _networkContext = NetworkContext()

    def __init__(self, networkcontext=NetworkContext()):
        self._networkContext = networkcontext

    def identify_domain_root(self, domain):
        return psl.get_public_suffix(domain)

    def identify_domain_connect_api(self, domain_root):
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

    def get_sync_url(self, config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlSyncUX' in config:
            return config['urlSyncUX'], None
        else:
            return None, 'No urlSyncUX in config'

    def get_async_url(self, config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlAsyncUX' in config:
            return config['urlAsyncUX'], None
        else:
            return None, 'No urlAsyncUX in config'

    def get_async_api_url(self, config: dict) -> (str, str):
        """

        :param config: domain connect config, see: DomainConnect.get_domain_config
        :return: (url, error text)
        """
        if 'urlAPI' in config:
            return config['urlAPI'], None
        else:
            return None, 'No urlAPI in config'

    def get_ux_size_url(self, config: dict) -> (str, str):
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
            return None, None, None, error
        else:
            ret, error2 = self._get_domain_config_for_root(domain_root, domain_connect_api)
            if (error2):
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

    def get_domain_connect_template_sync_url(self, domain, providerId, serviceId, redirect_uri=None, params={},  state=None):

        config, error = self.get_domain_config(domain)

        if (error is None):
            if config.urlSyncUX == None:
                return None, "No sync URL in config"

            sync_url_format = '{}/v2/domainTemplates/providers/{}/services/{}/' \
                              'apply?domain={}&host={}&{}'

            if (redirect_uri != None):
                params["redirect_uri"] = redirect_uri
            if (state != None):
                params["state"] = state

            return sync_url_format.format(config.urlSyncUX, providerId, serviceId, config.domain_root, config.host, urllib.parse.urlencode(params)), None
        else:
            return None, error

    def get_domain_connect_template_async_url(self, domain, providerId, serviceId, redirect_uri, params={},  state=None):

        config, error = self.get_domain_config(domain)

        if (error is None):
            if config.urlAsyncUX is None:
                return None, "No asynch UX URL in config"

            async_url_format = '{0}/v2/domainTemplates/providers/{1}' \
                              '?client_id={1}&scope={2}&domain={3}&host={4}&{5}'

            if (redirect_uri != None):
                params["redirect_uri"] = redirect_uri
            if (state != None):
                params["state"] = state

            return async_url_format.format(config.urlAsyncUX, providerId, serviceId, config.domain_root, config.host, urllib.parse.urlencode(params)), None
        else:
            return None, error
