__author__ = "Pawel Kowalik"
__copyright__ = "Copyright 2018, 1&1 Internet SE"
__credits__ = ["Andreea Dima"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Pawel Kowalik"
__email__ = "pawel-kow@users.noreply.github.com"
__status__ = "Beta"

from unittest2 import TestCase, skipIf
from domainconnect import DomainConnect, DomainConnectAsyncCredentials, TemplateNotSupportedException, \
    ConflictOnApplyException, NoDomainConnectRecordException
# to assure input works like raw_input in python 2
from builtins import input
import os.environ

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
        TEST_DOMAIN='weathernyc.nyc',
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
configs = [
    oneandone_config,
    godaddy_config
]


class TestDomainConnect(TestCase):

    def test_get_domain_connect_template_sync_url_invalid_domain(self):
        dc = DomainConnect()

        try:
            res = dc.get_domain_connect_template_sync_url('sfisdofjsoidhfiosdhif.bike', "exampleservice.domainconnect.org",
                                                      "template1",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"})
            assert False, "Got URL, where not possible: {}".format(res)
        except NoDomainConnectRecordException:
            pass

    def test_get_domain_connect_template_sync_url(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_get_domain_connect_template_sync_url(i)

    @staticmethod
    def _test_get_domain_connect_template_sync_url(config):

        dc = DomainConnect()

        # simple test sync
        res = dc.get_domain_connect_template_sync_url(domain=config['TEST_DOMAIN'],
                                                      provider_id="exampleservice.domainconnect.org",
                                                      service_id="template1",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"})
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply'
                  '?IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo&domain='
                + config['TEST_DOMAIN']), \
            "1. URL is different than expected: {}".format(res)



        # simple test sync with host
        res = dc.get_domain_connect_template_sync_url("justatest." + config['TEST_DOMAIN'],
                                                      "exampleservice.domainconnect.org",
                                                      "template1",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"})
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?'
                  'IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo&domain='
                + config['TEST_DOMAIN'] + '&host=justatest'), \
            "2. URL is different than expected: {}".format(res)

        # simple test sync with host and redirect uri and scope
        res = dc.get_domain_connect_template_sync_url(domain="justatest." + config['TEST_DOMAIN'],
                                                      provider_id="exampleservice.domainconnect.org",
                                                      service_id="template1",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                      redirect_uri="http://google.com", state="{name=value}")
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?'
                  'IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&domain=' + config['TEST_DOMAIN']
                + '&host=justatest&redirect_uri=http%3A%2F%2Fgoogle.com&state=%7Bname%3Dvalue%7D'), \
            "3. URL is different than expected: {}".format(res)

        # simple test sync with host and groupids
        res = dc.get_domain_connect_template_sync_url("justatest." + config['TEST_DOMAIN'],
                                                      "exampleservice.domainconnect.org",
                                                      "template1",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                      group_ids=['a', 'b'])
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?'
                  'IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&domain=' + config['TEST_DOMAIN']
                + '&groupId=a%2Cb'
                  '&host=justatest'), \
            "4. URL is different than expected: {}".format(res)

        # simple test template does not exist
        try:
            dc.get_domain_connect_template_sync_url(config['TEST_DOMAIN'], "exampleservice.domainconnect.org",
                                                    "template_not_exists",
                                                    params={"IP": "132.148.25.185",
                                                            "RANDOMTEXT": "shm:1531371203:Hejo"})
            assert False, "5. There is no error returned and was expected"
        except TemplateNotSupportedException:
            pass

    def test_get_domain_connect_template_sync_url_with_signature(self):

        dc = DomainConnect()
        config = oneandone_config

        # simple test sync and signature
        priv_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA18SgvpmeasN4BHkkv0SBjAzIc4grYLjiAXRtNiBUiGUDMeTzQrKTsWvy9NuxU1dIHCZy9o1CrKNg5EzLIZLNyMfI6qiXnM+HMd4byp97zs/3D39Q8iR5poubQcRaGozWx8yQpG0OcVdmEVcTfyR/XSEWC5u16EBNvRnNAOAvZYUdWqVyQvXsjnxQot8KcK0QP8iHpoL/1dbdRy2opRPQ2FdZpovUgknybq/6FkeDtW7uCQ6Mvu4QxcUa3+WP9nYHKtgWip/eFxpeb+qLvcLHf1h0JXtxLVdyy6OLk3f2JRYUX2ZZVDvG3biTpeJz6iRzjGg6MfGxXZHjI8weDjXrJwIDAQABAoIBAGiPedJDwXg9d1i7mCo0OY8z1qPeFh9OGP/Zet8i9bQPN2gjahslTNtK07cDC8C2aFRz8Xw3Ylsk5VxdNobzjFPDNUM6JhawnvR0jQU5GhdTwoc5DHH7aRRjTP6m938sRx0VrfZwfvJAB09Z4jHX7vyjfvprH9EH8GQ2L5lACtfnsSASVJB77H1vtgxTnum74CSqIck1MCjPD/TVUtYfMJwkUQWcbk79N4nvnEoagqsDrvw4okU2OYMWucQjyxfWTU4NGlsDScRbdDAb8sLr3DpMfXM8vpZJ3Ed6gfw14hEJym8XoHwDHmjGmgYH9iG6MODxuO5TLRmRR6b+jcUV/2kCgYEA4WGsDUO/NIXIqtDm5lTi5qeFl0sGKIgRLGuCrvjLF0Fq5Yx28wuow3OhZ3rbjlmhf9nUt24nUUY67plv2pi+vx3kVdbcNfk+Wkc0wfx8+U91qaTplMRhNjrnq/Kp9E7xtnzZRInpUG1Ha5ozTYobVvklUvjodFlF2c16Zz2X2AMCgYEA9RSeZm7oMyJbe985SScXruwt5ZXlUBoBLDZAeMloPpaqknFmSVSNgtniywztF8HppJQyiMvmUOUL2tKnuShXwsvTkCTBC/vNGXutiPS8O2yqeQ8dHoHuKcoMFwgajrbPrVkuFtUkjbQJ/TKoZtrxUdCryDZ/AHmRtiHh9E4NUQ0CgYAE7ngvSh4y7gJ4Cl4jCBR26492wgN+e4u0px2S6oq3FY1bPHmV09l7fVo4w21ubfOksoV/BgACPUEo216hL9psoCDQ6ASlgbCllQ1IeVfatKxka+FYift+jkdnccXaPKf5UD4Iy+O5CMsZRaR9u9nhS05PxHaBpTpsC5z0CVr7NQKBgQCsBTzpSQ9SVNtBpvzei8Hj1YKhkwTRpG8OSUYXgcbZp4cyIsZY0jBBmA3H19rSwhjsm9icjAGs5hfcD+AJ5nczEz37/tBBSQw8xsKXTrCQRUWikyktMKWqT1cNE3MQmOBMHDxtak2t6KDaR6RMDYE0m/L3JMkf3DSaUk323JIcQQKBgD6lHhw79Cenpezzf0566uWE1QF6Sv3kWk6Gkzo2jUGmjo2tG1v2Nj82DvcTuqvfUKSr2wTKINxnKGyYXGto0BykdxeFbR04cNcBB46zUjasro2ZCvIoAHCpohNBI2dL6dI+RI3jC/KY3jPNI0toaOTWkeAvJ7w09G2ttlv8qLNV\n-----END RSA PRIVATE KEY-----'
        res = dc.get_domain_connect_template_sync_url(domain=config['TEST_DOMAIN'],
                                                      provider_id="exampleservice.domainconnect.org",
                                                      service_id="template2",
                                                      params={"IP": "132.148.25.185",
                                                              "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                      sign=True,
                                                      private_key=priv_key,
                                                      keyid='_dck1')
        assert (res == config['SYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template2/apply'
                  '?IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo&domain='
                + config['TEST_DOMAIN']
                + '&sig=E8lWecXOM7s4SwLp6bNhivmvqV47wynek6rO13iUIbC095p9WR5VnCY%2Fg8aUhazmM3squI0lr1wz5REiUIHVX5AP3reFbU6bLIzckgWoN9%2F3VgxtS9q%2FEgO8HL9%2FbTGjUodf9eI7afWXR348C8ekQFZeT%2F7SHMn7VvM%2BEpLA7ZDIq4kROJXE2eIOI21j6nkE4luWn2vWYdK%2BvUnp4YTzot03uj6cQ5nkpEziCJK5hqMqhZP5%2F755RLI3bH%2BpMvegFE2ualUM6BsvNJ4kyYNf250NyafLZU1RbkeUD1SM4KaUU59IY1PEKI44I21%2BfCPN8kAMFmTJqpNHLNffixNlgA%3D%3D&key=_dck1'), \
            "URL is different than expected: {}".format(res)

    def test_generate_sig_params(self):
        priv_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA18SgvpmeasN4BHkkv0SBjAzIc4grYLjiAXRtNiBUiGUDMeTzQrKTsWvy9NuxU1dIHCZy9o1CrKNg5EzLIZLNyMfI6qiXnM+HMd4byp97zs/3D39Q8iR5poubQcRaGozWx8yQpG0OcVdmEVcTfyR/XSEWC5u16EBNvRnNAOAvZYUdWqVyQvXsjnxQot8KcK0QP8iHpoL/1dbdRy2opRPQ2FdZpovUgknybq/6FkeDtW7uCQ6Mvu4QxcUa3+WP9nYHKtgWip/eFxpeb+qLvcLHf1h0JXtxLVdyy6OLk3f2JRYUX2ZZVDvG3biTpeJz6iRzjGg6MfGxXZHjI8weDjXrJwIDAQABAoIBAGiPedJDwXg9d1i7mCo0OY8z1qPeFh9OGP/Zet8i9bQPN2gjahslTNtK07cDC8C2aFRz8Xw3Ylsk5VxdNobzjFPDNUM6JhawnvR0jQU5GhdTwoc5DHH7aRRjTP6m938sRx0VrfZwfvJAB09Z4jHX7vyjfvprH9EH8GQ2L5lACtfnsSASVJB77H1vtgxTnum74CSqIck1MCjPD/TVUtYfMJwkUQWcbk79N4nvnEoagqsDrvw4okU2OYMWucQjyxfWTU4NGlsDScRbdDAb8sLr3DpMfXM8vpZJ3Ed6gfw14hEJym8XoHwDHmjGmgYH9iG6MODxuO5TLRmRR6b+jcUV/2kCgYEA4WGsDUO/NIXIqtDm5lTi5qeFl0sGKIgRLGuCrvjLF0Fq5Yx28wuow3OhZ3rbjlmhf9nUt24nUUY67plv2pi+vx3kVdbcNfk+Wkc0wfx8+U91qaTplMRhNjrnq/Kp9E7xtnzZRInpUG1Ha5ozTYobVvklUvjodFlF2c16Zz2X2AMCgYEA9RSeZm7oMyJbe985SScXruwt5ZXlUBoBLDZAeMloPpaqknFmSVSNgtniywztF8HppJQyiMvmUOUL2tKnuShXwsvTkCTBC/vNGXutiPS8O2yqeQ8dHoHuKcoMFwgajrbPrVkuFtUkjbQJ/TKoZtrxUdCryDZ/AHmRtiHh9E4NUQ0CgYAE7ngvSh4y7gJ4Cl4jCBR26492wgN+e4u0px2S6oq3FY1bPHmV09l7fVo4w21ubfOksoV/BgACPUEo216hL9psoCDQ6ASlgbCllQ1IeVfatKxka+FYift+jkdnccXaPKf5UD4Iy+O5CMsZRaR9u9nhS05PxHaBpTpsC5z0CVr7NQKBgQCsBTzpSQ9SVNtBpvzei8Hj1YKhkwTRpG8OSUYXgcbZp4cyIsZY0jBBmA3H19rSwhjsm9icjAGs5hfcD+AJ5nczEz37/tBBSQw8xsKXTrCQRUWikyktMKWqT1cNE3MQmOBMHDxtak2t6KDaR6RMDYE0m/L3JMkf3DSaUk323JIcQQKBgD6lHhw79Cenpezzf0566uWE1QF6Sv3kWk6Gkzo2jUGmjo2tG1v2Nj82DvcTuqvfUKSr2wTKINxnKGyYXGto0BykdxeFbR04cNcBB46zUjasro2ZCvIoAHCpohNBI2dL6dI+RI3jC/KY3jPNI0toaOTWkeAvJ7w09G2ttlv8qLNV\n-----END RSA PRIVATE KEY-----'
        querystring = 'domain=connect.domains&RANDOMTEXT=shm%3A1552462554%3AHola&IP=132.148.25.185'

        sigparams = DomainConnect._generate_sig_params(querystring, priv_key, '_dck1')

        assert (sigparams == '&sig=pDgKCqDX%2BYafD8fqchYjayZt6bgf5ncz%2FJlYVGV0SbZrcUPb5tgMyqpn4g%2BlY%2FigpgKYFhkXGcAeNOrQ0aiTu31bLo7ODkK2fWsdz4G%2BpSa5Lkb7NhwS07o6cpQMcvO8aihA7pU5%2BIbPd3Im1ncUNol3zfjeyAl%2BaBkfcXOAl2xnWY8NobMzaI0jqVwPnWperRj5VGfX6vu5mPviDFzcS0RvruRAHv08X8zDp%2BBvCnpk4L1cWn49%2FZceS8Hifo7%2FkVd4j%2BdFGvze7H4cGZ2Kx6ZrSShW3a7AwvV6cVGxqn%2FdQlpYYsHBHlv9Zbhe2pKuqpAhB%2FxDN2G%2FjQaDqmcWGw%3D%3D&key=_dck1'), \
            "Generated signature parameters differ"


    def test_get_domain_config(self):
        for i in configs:
            with self.subTest(i=i):
                self._test_get_domain_config(i)

    @staticmethod
    def _test_get_domain_config(config):
        dc = DomainConnect()
        res = dc.get_domain_config('testhost.' + config['TEST_DOMAIN'])
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
        res = dc.get_domain_connect_template_async_context(
            config['TEST_DOMAIN'], "exampleservice.domainconnect.org", "template2",
            params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
            redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
            state="{name=value}")
        assert (res.asyncConsentUrl == config['ASYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                  '?client_id=exampleservice.domainconnect.org&scope=template2&domain='
                + config['TEST_DOMAIN']
                + '&host=&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2F'
                  'async_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res)

        # simple test sync with host
        res = dc.get_domain_connect_template_async_context(
            "justatest." + config['TEST_DOMAIN'],
            "exampleservice.domainconnect.org", "template2",
            params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
            redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
            state="{name=value}")
        assert (res.asyncConsentUrl == config['ASYNC_URL']
                + '/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                  '?client_id=exampleservice.domainconnect.org&scope=template2&domain='
                + config['TEST_DOMAIN']
                + '&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                  '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2F'
                  'async_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res[0])

        # simple test template does not exist
        try:
            dc.get_domain_connect_template_async_context(
                config['TEST_DOMAIN'], "exampleservice.domainconnect.org",
                "template_not_exists",
                params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
                redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response")
            assert False, "There is no error returned and was expected"
        except TemplateNotSupportedException:
            pass

    @skipIf("CI" in os.environ)
    def test_get_domain_connect_async_open_browser(self):
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_open_domain_connect_template_asynclink(i)

    @staticmethod
    def _test_open_domain_connect_template_asynclink(config):
        params = {"IP": "132.148.25.185",
                  "RANDOMTEXT": "shm:1531371203:Hejo async"}

        dc = DomainConnect()
        context = dc.open_domain_connect_template_asynclink(
            'asyncpage.' + config['TEST_DOMAIN'],
            'exampleservice.domainconnect.org',
            'template2', params=params,
            redirect_uri='https://exampleservice.domainconnect.org/async_oauth_response',
            service_id_in_path=config['ASYNC_SERVICE_IN_PATH'])

        code = input("Please enter code: ")
        context.code = code

        ctx = dc.get_async_token(context, test_credentials[context.config.providerName])
        assert (ctx.access_token is not None), 'Access token missing'
        assert (ctx.access_token_expires_in is not None), 'Access token expiration data missing'
        assert (ctx.iat is not None), 'Access token iat missing'

        dc.apply_domain_connect_template_async(context, params=params)

    @skipIf("CI" in os.environ)
    def test_get_domain_connect_async_token_refresh(self):
        dc = DomainConnect()
        for i in configs:
            with self.subTest(i=i):
                TestDomainConnect._test_get_domain_connect_async_token_refresh(i)

    @staticmethod
    def _test_get_domain_connect_async_token_refresh(config):
        params = {"IP": "132.148.25.185"}

        dc = DomainConnect()
        # use of DynDNS to always have refresh_token onboarded
        context = dc.open_domain_connect_template_asynclink(
            'asyncpage.' + config['TEST_DOMAIN'],
            'domainconnect.org',
            'dynamicdns', params=params,
            redirect_uri='https://dynamicdns.domainconnect.org/ddnscode',
            service_id_in_path=config['ASYNC_SERVICE_IN_PATH'])

        code = input("Please enter code: ")
        context.code = code

        # for DYNDNS there are static credentials
        credentials = DomainConnectAsyncCredentials(client_id='domainconnect.org',
                                           client_secret='inconceivable',
                                           api_url=context.config.urlAPI)
        ctx = dc.get_async_token(context, credentials)
        initial_token = ctx.access_token
        assert (ctx.access_token_expires_in is not None), 'Access token expiration data missing'
        assert (ctx.iat is not None), 'Access token iat missing'
        assert (ctx.refresh_token is not None), 'Refresh token missing'
        ctx.access_token_expires_in = 1

        ctx = dc.get_async_token(ctx, credentials)
        assert (initial_token != ctx.access_token), "Token not refreshed when expired"

    @skipIf("CI" in os.environ)
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
        context = dc.open_domain_connect_template_asynclink(
            domain='asyncpage-conflict.' + config['TEST_DOMAIN'],
            provider_id='exampleservice.domainconnect.org',
            service_id=['template1', 'template2'], params=params,
            redirect_uri='https://exampleservice.domainconnect.org/async_oauth_response',
            service_id_in_path=config['ASYNC_SERVICE_IN_PATH'])

        code = input("Please enter code: ")
        context.code = code

        ctx = dc.get_async_token(context, test_credentials[context.config.providerName])
        assert (ctx.access_token is not None), 'Access token missing'
        assert (ctx.access_token_expires_in is not None), 'Access token expiration data missing'

        dc.apply_domain_connect_template_async(context, service_id='template1', params=params, force=True)

        try:
            dc.apply_domain_connect_template_async(
                context, service_id='template2',
                params=params2)
            assert False, '2. No error on apply'
        except ConflictOnApplyException:
            pass

        dc.apply_domain_connect_template_async(context, service_id='template2', params=params2, force=True)
