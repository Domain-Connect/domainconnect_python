from unittest2 import TestCase
from domainconnect import DomainConnect, DomainConnectAsyncCredentials
# to assure input works like raw_input in python 2
from builtins import input

oneandone_config = \
    dict(
        PROVIDER_ID='1and1',
        TEST_DOMAIN='connect.domains',
        SYNC_URL='https://domainconnect.1and1.com/sync',
        ASYNC_URL='https://domainconnect.1and1.com/async',
        ASYNC_SERVICE_IN_PATH=False,
        API_URL='https://api.domainconnect.1and1.com'
    )

godaddy_config = \
    dict(
        PROVIDER_ID='GoDaddy',
        TEST_DOMAIN='cuco240714it.today',
        SYNC_URL='https://dcc.godaddy.com/manage',
        ASYNC_URL='https://dcc.godaddy.com/manage',
        ASYNC_SERVICE_IN_PATH=True,
        API_URL='https://domainconnect.api.godaddy.com'
    )

test_credentials = {
    "1and1": DomainConnectAsyncCredentials(client_id='exampleservice.domainconnect.org',
                                           client_secret='cd$;CVZRj#B8C@o3o8E4v-*k2H7S%)',
                                           api_url=oneandone_config['API_URL']),
    "GoDaddy": DomainConnectAsyncCredentials(client_id='exampleservice.domainconnect.org',
                                             client_secret='DomainConnectGeheimnisSecretString',
                                             api_url=godaddy_config['API_URL']),
}

configs = [oneandone_config, godaddy_config]


class TestDomainConnect(TestCase):

    def test_get_domain_connect_template_sync_url(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_get_domain_connect_template_sync_url(i)

    @staticmethod
    def _test_get_domain_connect_template_sync_url(config):

        dc = DomainConnect()

        # simple test sync
        res, error = dc.get_domain_connect_template_sync_url(config['TEST_DOMAIN'], "exampleservice.domainconnect.org",
                                                             "template1",
                                                             params={"IP": "132.148.25.185",
                                                                     "RANDOMTEXT": "shm:1531371203:Hejo"})
        assert (error is None), "1. There is an error returned: {}".format(error)
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain='
                + config['TEST_DOMAIN'] + '&host=&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'), \
            "1. URL is different than expected: {}".format(res)

        # simple test sync with host
        res, error = dc.get_domain_connect_template_sync_url("justatest." + config['TEST_DOMAIN'],
                                                             "exampleservice.domainconnect.org",
                                                             "template1",
                                                             params={"IP": "132.148.25.185",
                                                                     "RANDOMTEXT": "shm:1531371203:Hejo"})
        print(res)
        assert (error is None), "2. There is an error returned: {}".format(error)
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain='
                + config['TEST_DOMAIN'] + '&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'), \
            "2. URL is different than expected: {}".format(res)

        # simple test sync with host and redirect uri and scope
        res, error = dc.get_domain_connect_template_sync_url("justatest." + config['TEST_DOMAIN'],
                                                             "exampleservice.domainconnect.org",
                                                             "template1",
                                                             params={"IP": "132.148.25.185",
                                                                     "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                             redirect_uri="http://google.com", state="{name=value}")
        assert (error is None), "3. There is an error returned: {}".format(error)
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain='
                + config['TEST_DOMAIN']
                + '&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&redirect_uri=http%3A%2F%2Fgoogle.com&state=%7Bname%3Dvalue%7D'), \
            "3. URL is different than expected: {}".format(res)

        # simple test sync with host and groupids
        res, error = dc.get_domain_connect_template_sync_url("justatest." + config['TEST_DOMAIN'],
                                                             "exampleservice.domainconnect.org",
                                                             "template1",
                                                             params={"IP": "132.148.25.185",
                                                                     "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                             group_ids=['a', 'b'])
        assert (error is None), "4. There is an error returned: {}".format(error)
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain='
                + config['TEST_DOMAIN']
                + '&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&groupId=a%2Cb'), \
            "4. URL is different than expected: {}".format(res)

        # simple test template does not exits
        res, error = dc.get_domain_connect_template_sync_url(config['TEST_DOMAIN'], "exampleservice.domainconnect.org",
                                                             "template_not_exists",
                                                             params={"IP": "132.148.25.185",
                                                                     "RANDOMTEXT": "shm:1531371203:Hejo"})
        assert (error is not None), "5. There is no error returned and was expected"
        assert (res is None), "5. There was no url expected and came: {}".format(res)

    def test_get_domain_config(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_get_domain_config(i)

    @staticmethod
    def _test_get_domain_config(config):
        dc = DomainConnect()
        res, error = dc.get_domain_config('testhost.' + config['TEST_DOMAIN'])
        assert (error is None), 'There is an error returned'
        assert (res.domain_root == config['TEST_DOMAIN']), 'Domain root wrong: {}'.format(res.domain_root)
        assert (res.host == 'testhost'), 'Host not correct: {}'.format(res.host)
        assert (res.urlSyncUX == config['SYNC_URL']), 'urlSyncUX not correct: {}'.format(res.urlSyncUX)
        assert (res.urlAsyncUX == config['ASYNC_URL']), 'urlAsyncUX not correct: {}'.format(res.urlAsyncUX)
        assert (res.urlAPI == config['API_URL']), 'urlAPI not correct: {}'.format(res.urlAPI)
        assert (res.providerName == config['PROVIDER_ID']), 'providerName not correct: {}'.format(res.providerName)

    def test_get_domain_connect_template_async_url(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_get_domain_connect_template_async_url(i)

    @staticmethod
    def _test_get_domain_connect_template_async_url(config):
        dc = DomainConnect()

        # simple test sync without host
        res, error = dc.get_domain_connect_template_async_context(
            config['TEST_DOMAIN'], "exampleservice.domainconnect.org", "template2",
            params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
            redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
            state="{name=value}")
        print(res)
        assert (error is None), "There is an error returned: {}".format(error)
        assert (res.asyncConsentUrl == config['ASYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                  '?client_id=exampleservice.domainconnect.org&scope=template2&domain='
                + config['TEST_DOMAIN']
                + '&host=&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2F'
                  'async_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res)

        # simple test sync with host
        res, error = dc.get_domain_connect_template_async_context(
            "justatest." + config['TEST_DOMAIN'],
            "exampleservice.domainconnect.org", "template2",
            params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
            redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
            state="{name=value}")
        print(res)
        assert (error is None), "There is an error returned"
        assert (res.asyncConsentUrl == config['ASYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                  '?client_id=exampleservice.domainconnect.org&scope=template2&domain='
                + config['TEST_DOMAIN']
                + '&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2F'
                  'async_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res[0])

        # simple test template does not exits
        res, error = dc.get_domain_connect_template_async_context(
            config['TEST_DOMAIN'], "exampleservice.domainconnect.org",
            "template_not_exists",
            params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
            redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response")
        print(res)
        assert (error is not None), "There is no error returned and was expected"
        assert (res is None), "There was no url expected: {}".format(res.asyncConsentUrl)

    def test_get_domain_connect_async_open_browser(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_open_domain_connect_template_asynclink(i)

    @staticmethod
    def _test_open_domain_connect_template_asynclink(config):
        params = {"IP": "132.148.25.185",
                  "RANDOMTEXT": "shm:1531371203:Hejo async"}

        dc = DomainConnect()
        context, error = dc.open_domain_connect_template_asynclink(
            'asyncpage.' + config['TEST_DOMAIN'],
            'exampleservice.domainconnect.org',
            'template2', params=params,
            redirect_uri='https://exampleservice.domainconnect.org/async_oauth_response',
            service_id_in_path=config['ASYNC_SERVICE_IN_PATH'])

        assert (error is None), "Error occured: {}".format(error)

        code = input("Please enter code: ")
        context.code = code

        ctx, error = dc.get_async_token(context, test_credentials[context.config.providerName])
        assert (error is None), "Error occured: {}".format(error)
        assert (ctx.access_token is not None), 'Access token missing'
        assert (ctx.access_token_expires_in is not None), 'Access token expiration data missing'

        res, error = dc.apply_domain_connect_template_async(context, params=params)
        assert error is None, 'Error on apply: {}'.format(error)
        assert res == 'Success', 'Wrong result: {}'.format(res)

    def test_get_domain_connect_async_conflict(self):
        for i in configs:
            with self.subTest(i=i):
                self._test_get_domain_connect_async_conflict(i)

    @staticmethod
    def _test_get_domain_connect_async_conflict(config):
        if config["ASYNC_SERVICE_IN_PATH"]:
            print("Skipping test as service in path does not support multiple templates in consent: {}".format(config))
            return

        params = {"IP": "132.148.25.184", "RANDOMTEXT": "shm:1531371203:Hejo async"}
        params2 = {"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo async in conflict"}

        dc = DomainConnect()
        context, error = dc.open_domain_connect_template_asynclink(
            'asyncpage-conflict.' + config['TEST_DOMAIN'],
            'exampleservice.domainconnect.org',
            ['template1', 'template2'], params=params,
            redirect_uri='https://exampleservice.domainconnect.org/async_oauth_response',
            service_id_in_path=config['ASYNC_SERVICE_IN_PATH'])

        assert (error is None), "Error occured: {}".format(error)

        code = input("Please enter code: ")
        context.code = code

        ctx, error = dc.get_async_token(context, test_credentials[context.config.providerName])
        assert (error is None), "Error occured: {}".format(error)
        assert (ctx.access_token is not None), 'Access token missing'
        assert (ctx.access_token_expires_in is not None), 'Access token expiration data missing'

        res, error = dc.apply_domain_connect_template_async(context, service_id='template1', params=params, force=True)
        assert error is None, '1. Error on apply: {}'.format(error)
        assert res == 'Success', '1. Wrong result: {}'.format(res)

        res, error = dc.apply_domain_connect_template_async(
            context, service_id='template2',
            params=params2)
        assert error is not None, '2. No error on apply'
        assert res == 'Conflict', '2. We expected an error, got: {}'.format(res)

        res, error = dc.apply_domain_connect_template_async(context, service_id='template2', params=params2, force=True)
        assert error is None, '3. Error on apply: {}'.format(error)
        assert res == 'Success', '3. Wrong result: {}'.format(res)
