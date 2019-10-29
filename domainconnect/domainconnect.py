__author__ = "Pawel Kowalik"
__copyright__ = "Copyright 2018, 1&1 Internet SE"
__credits__ = ["Andreea Dima"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Pawel Kowalik"
__email__ = "pawel-kow@users.noreply.github.com"
__status__ = "Beta"

import logging
import json
import time
from six.moves import urllib
from dns.exception import Timeout
from dns.resolver import Resolver, NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers
from publicsuffixlist import PublicSuffixList
import webbrowser
from .network import get_json, get_http, http_request_json, NetworkContext

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from base64 import b64decode, b64encode

logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

psl = PublicSuffixList()


class DomainConnectException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TemplateDoesNotExistException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class NoDomainConnectRecordException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class NoDomainConnectSettingsException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class InvalidDomainConnectSettingsException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class TemplateNotSupportedException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class ConflictOnApplyException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class ApplyException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class AsyncTokenException(DomainConnectException):
    def __init__(self, *args, **kwargs):
        DomainConnectException.__init__(self, *args, **kwargs)


class DomainConnectConfig:
    # TODO: implement serialization and deserialization to JSON
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
    iat = None
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
    _resolver = Resolver()

    def __init__(self, networkcontext=NetworkContext()):
        self._networkContext = networkcontext
        if networkcontext.nameservers is not None:
            self._resolver.nameservers = networkcontext.nameservers.split(',')

    @staticmethod
    def identify_domain_root(domain):
        return psl.privatesuffix(domain)

    def _identify_domain_connect_api(self, domain_root):
        # noinspection PyBroadException
        try:
            dns = self._resolver.query('_domainconnect.{}'.format(domain_root), 'TXT')
            domain_connect_api = str(dns[0]).replace('"', '')
            logger.debug('Domain Connect API {} for {} found.'.format(domain_connect_api, domain_root))
            return domain_connect_api
        except Timeout:
            logger.debug('Timeout. Failed to find Domain Connect API for "{}"'.format(domain_root))
            raise NoDomainConnectRecordException(
                'Timeout. Failed to find Domain Connect API for "{}"'.format(domain_root))
        except NXDOMAIN or YXDOMAIN:
            logger.debug('Failed to resolve "{}"'.format(domain_root))
            raise NoDomainConnectRecordException('Failed to resolve "{}"'.format(domain_root))
        except NoAnswer:
            logger.debug('No Domain Connect API found for "{}"'.format(domain_root))
            raise NoDomainConnectRecordException('No Domain Connect API found for "{}"'.format(domain_root))
        except NoNameservers:
            logger.debug('No nameservers avalaible for "{}"'.format(domain_root))
            raise NoDomainConnectRecordException('No nameservers avalaible for "{}"'.format(domain_root))
        except Exception:
            pass
        logger.debug('No Domain Connect API found for "{}"'.format(domain_root))
        raise NoDomainConnectRecordException('No Domain Connect API found for "{}"'.format(domain_root))

    def get_domain_config(self, domain):
        """Makes a discovery of domain name and resolves configuration of DNS provider

        :param domain: str
            domain name
        :return: DomainConnectConfig
            domain connect config
        :raises: NoDomainConnectRecordException
            when no _domainconnect record found
        :raises: NoDomainConnectSettingsException
            when settings are not found
        """
        domain_root = self.identify_domain_root(domain)

        host = ''
        if len(domain_root) != len(domain):
            host = domain.replace('.' + domain_root, '')

        domain_connect_api = self._identify_domain_connect_api(domain_root)

        ret = self._get_domain_config_for_root(domain_root, domain_connect_api)
        return DomainConnectConfig(domain, domain_root, host, ret)

    def _get_domain_config_for_root(self, domain_root, domain_connect_api):
        """

        :param domain_root: str
            domain name for zone root
        :param domain_connect_api: str
            URL of domain connect API of the vendor
        :return: dict
            domain connect config
        :raises: NoDomainConnectRecordException
            when no _domainconnect record found
        :raises: NoDomainConnectSettingsException
            when settings are not found
        """
        url = 'https://{}/v2/{}/settings'.format(domain_connect_api, domain_root)
        try:
            response = get_json(self._networkContext, url)
            logger.debug('Domain Connect config for {} over {}: {}'.format(domain_root, domain_connect_api,
                                                                           response))
            return response
        except Exception as e:
            logger.debug("Exception when getting config:{}".format(e))
        logger.debug('No Domain Connect config found for {}.'.format(domain_root))
        raise NoDomainConnectSettingsException('No Domain Connect config found for {}.'.format(domain_root))

    # Generates a signature on the passed in data
    @staticmethod
    def _generate_sig(private_key, data):
        pk = serialization.load_pem_private_key(
            private_key.encode(),
            password=None,
            backend=default_backend()
        )

        sig = pk.sign(
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return b64encode(sig)

    @staticmethod
    def _generate_sig_params(queryparams, private_key=None, keyid=None):
        if private_key is None or keyid is None:
            raise InvalidDomainConnectSettingsException("Private key and/or key ID not provided for signing")
        signature = DomainConnect._generate_sig(private_key, queryparams)
        return '&' + urllib.parse.urlencode(
            {
                "sig": signature,
                "key": keyid,
            }
        )

    def check_template_supported(self, config, provider_id, service_ids):
        """

        :param config: DomainConnectConfig
            domain connect config
        :param provider_id: str
            provider_id to check
        :param service_ids: str
            service_id to check
        :return: (dict, str)
            (template supported, error)
        :raises: TemplateNotSupportedException
            when template is not supported
        """

        if type(service_ids) != list:
            service_ids = [service_ids]

        for service_id in service_ids:
            url = '{}/v2/domainTemplates/providers/{}/services/{}' \
                .format(config.urlAPI, provider_id, service_id)

            try:
                response = get_http(self._networkContext, url)
                logger.debug('Template for serviceId: {} from {}: {}'.format(service_id, provider_id,
                                                                             response))
            except Exception as e:
                logger.debug("Exception when getting config:{}".format(e))
                raise TemplateNotSupportedException(
                    'No template for serviceId: {} from {}'.format(service_id, provider_id))


    def get_domain_connect_template_sync_url(self, domain, provider_id, service_id, redirect_uri=None, params=None,
                                             state=None, group_ids=None, sign=False, private_key=None, keyid=None):
        """Makes full Domain Connect discovery of a domain and returns full url to request sync consent.

        :param domain: str
        :param provider_id: str
        :param service_id: str
        :param redirect_uri: str
        :param params: dict
        :param state: str
        :param group_ids: list(str)
        :param sign: bool
        :param private_key: str - RSA key in PEM format
        :param keyid: str - host name of the TXT record with public KEY (appended to syncPubKeyDomain)
        :return: (str, str)
            first field is an url which shall be used to redirect the browser to
            second field is an indication of error
        :raises: NoDomainConnectRecordException
            when no _domainconnect record found
        :raises: NoDomainConnectSettingsException
            when settings are not found
        :raises: InvalidDomainConnectSettingsException
            when settings contain missing fields
        """
        # TODO: support for provider_name (for shared templates)

        if params is None:
            params = {}

        config = self.get_domain_config(domain)

        self.check_template_supported(config, provider_id, service_id)

        if config.urlSyncUX is None:
            raise InvalidDomainConnectSettingsException("No sync URL in config")

        sync_url_format = '{}/v2/domainTemplates/providers/{}/services/{}/' \
                          'apply?{}{}'

        params['domain'] = config.domain_root
        if config.host is not None and config.host != '':
            params['host'] = config.host
        if redirect_uri is not None:
            params["redirect_uri"] = redirect_uri
        if state is not None:
            params["state"] = state
        if group_ids is not None:
            params["groupId"] = ",".join(group_ids)

        queryparams = urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0]))
        sigparams = DomainConnect._generate_sig_params(queryparams, private_key, keyid) if sign else ''

        return sync_url_format.format(config.urlSyncUX, provider_id, service_id, queryparams, sigparams)

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
        :raises: NoDomainConnectRecordException
            when no _domainconnect record found
        :raises: NoDomainConnectSettingsException
            when settings are not found
        :raises: TemplateNotSupportedException
            when template is not found
        :raises: InvalidDomainConnectSettingsException
            when parts of the settings are missing
        :raises: DomainConnectException
            on other domain connect issues
        """
        if params is None:
            params = {}

        config = self.get_domain_config(domain)

        self.check_template_supported(config, provider_id, service_id)

        if config.urlAsyncUX is None:
            raise InvalidDomainConnectSettingsException("No asynch UX URL in config")

        if service_id_in_path:
            if type(service_id) is list:
                raise DomainConnectException("Multiple services are only supported with service_id_in_path=false")
            async_url_format = '{0}/v2/domainTemplates/providers/{1}/services/{2}' \
                               '?client_id={1}&scope={2}&domain={3}&host={4}&{5}'
        else:
            if type(service_id) is list:
                service_id = '+'.join(service_id)
            async_url_format = '{0}/v2/domainTemplates/providers/{1}' \
                               '?client_id={1}&scope={2}&domain={3}&host={4}&{5}'

        if redirect_uri is not None:
            params["redirect_uri"] = redirect_uri
        if state is not None:
            params["state"] = state

        ret = DomainConnectAsyncContext(config, provider_id, service_id, redirect_uri, params)
        ret.asyncConsentUrl = async_url_format.format(config.urlAsyncUX, provider_id, service_id,
                                                      config.domain_root, config.host,
                                                      urllib.parse.urlencode(
                                                          sorted(params.items(), key=lambda val: val[0])))
        return ret

    def open_domain_connect_template_asynclink(self, domain, provider_id, service_id, redirect_uri, params=None,
                                               state=None, service_id_in_path=False):
        """

        :param domain:
        :param provider_id:
        :param service_id:
        :param redirect_uri:
        :param params:
        :param state:
        :param service_id_in_path:
        :return:
        :raises: NoDomainConnectRecordException
            when no _domainconnect record found
        :raises: NoDomainConnectSettingsException
            when settings are not found
        :raises: TemplateNotSupportedException
            when template is not found
        :raises: InvalidDomainConnectSettingsException
            when parts of the settings are missing
        :raises: DomainConnectException
            on other domain connect issues

        """
        if params is None:
            params = {}
        async_context = self.get_domain_connect_template_async_context(
            domain, provider_id, service_id, redirect_uri, params, state, service_id_in_path)

        try:
            print('Please open URL: {}'.format(async_context.asyncConsentUrl))
            webbrowser.open_new_tab(async_context.asyncConsentUrl)
            return async_context
        except webbrowser.Error as err:
            raise Exception("Error opening browser window: {}".format(err))

    def get_async_token(self, context, credentials):
        """Gets access_token in async process

        :param context: DomainConnectAsyncContext
        :param credentials: DomainConnectAsyncCredentials
        :return: DomainConnectAsyncContext
            context enriched with access_token and refresh_token if existing
        :raises: AsyncTokenException
        """
        params = {'code': context.code, 'grant_type': 'authorization_code'}
        if getattr(context, 'iat', None) and getattr(context, 'access_token_expires_in', None) and \
                getattr(context, 'refresh_token', None):
            now = int(time.time()) + 60
            if now > context.iat + context.access_token_expires_in:
                params = {'refresh_token': context.refresh_token, 'grant_type': 'refresh_token',
                          'client_id': credentials.client_id, 'client_secret': credentials.client_secret
                }
            else:
                logger.debug('Context has a valid access token')
                return context
        params['redirect_uri'] = context.return_url

        url_get_access_token = '{}/v2/oauth/access_token?{}'.format(context.config.urlAPI,
                                                                    urllib.parse.urlencode(
                                                                        sorted(params.items(), key=lambda val: val[0])))
        try:
            # this has to be checked to avoid secret leakage by spoofed "settings" end-point
            if credentials.api_url != context.config.urlAPI:
                raise AsyncTokenException("URL API for provider does not match registered one with credentials")
            data, status = http_request_json(self._networkContext,
                                             method='POST',
                                             content_type='application/json',
                                             body=json.dumps({
                                                 'client_id': credentials.client_id,
                                                 'client_secret': credentials.client_secret,
                                             }),
                                             url=url_get_access_token
                                             )
        except Exception as ex:
            logger.debug('Cannot get async token: {}'.format(ex))
            raise AsyncTokenException('Cannot get async token: {}'.format(ex))

        if 'access_token' not in data \
                or 'expires_in' not in data \
                or 'token_type' not in data \
                or data['token_type'].lower() != 'bearer':
            logger.debug('Token not complete: {}'.format(data))
            raise AsyncTokenException('Token not complete: {}'.format(data))

        context.access_token = data['access_token']
        context.access_token_expires_in = data['expires_in']
        context.iat = int(time.time())

        if 'refresh_token' in data:
            context.refresh_token = data['refresh_token']

        return context

    def apply_domain_connect_template_async(self, context, host=None, service_id=None,
                                            params=None, force=False, group_ids=None):
        """

        :param context: DomainConnectAsyncContext
        :param host: str
        :param service_id:
        :param params:
        :param force:
        :param group_ids: list(str)
        :return: None
        :raises: ConflictOnApply
            Conflict situation
        :raises: ApplyException
            Other errors in apply operation
        """
        if params is None:
            params = {}
        if host is None:
            host = context.config.host
        if service_id is None:
            service_id = context.serviceId
        if group_ids is not None:
            params["groupId"] = ",".join(group_ids)

        async_url_format = '{}/v2/domainTemplates/providers/{}/services/{}/' \
                           'apply?domain={}&host={}&{}'

        if force:
            params['force'] = 'true'

        url = async_url_format.format(context.config.urlAPI, context.providerId, service_id, context.config.domain_root,
                                      host, urllib.parse.urlencode(sorted(params.items(), key=lambda val: val[0])))

        try:
            res, status = http_request_json(self._networkContext, 'POST', url, bearer=context.access_token,
                                            accepted_statuses=[200, 202, 409])
            if status in [409]:
                raise ConflictOnApplyException("Conflict: {}".format(res))
        except ConflictOnApplyException:
            raise
        except Exception as e:
            raise ApplyException('Error on apply: {}'.format(e))

    # TODO: implement revert
