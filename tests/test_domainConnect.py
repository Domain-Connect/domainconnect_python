from unittest import TestCase
from domainconnect import *


class TestDomainConnect(TestCase):
    def test_get_domain_connect_template_sync_url(self):
        dc = DomainConnect()

        # simple test sync
        res = dc.get_domain_connect_template_sync_url("connect.domains", "exampleservice.domainconnect.org",
                                                          "template1", params={"IP": "132.148.25.185",
                                                                               "RANDOMTEXT": "shm:1531371203:Hejo"})
        print(res)
        assert (res[1] is None), "There is an error returned"
        assert (res[0] == 'https://domainconnect.1and1.com/sync/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain=connect.domains&host=&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'), "URL is different than expected"

        #simple test sync with host
        res = dc.get_domain_connect_template_sync_url("justatest.connect.domains", "exampleservice.domainconnect.org", "template1", params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"})
        print(res)
        assert(res[1] is None), "There is an error returned"
        assert(res[0] == 'https://domainconnect.1and1.com/sync/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain=connect.domains&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'), "URL is different than expected"

        #simple test sync with host and redirect uri and scope
        res = dc.get_domain_connect_template_sync_url("justatest.connect.domains", "exampleservice.domainconnect.org", "template1", params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"}, redirect_uri="http://google.com", state="{name=value}")
        print(res)
        assert(res[1] is None), "There is an error returned"
        assert(res[0] == 'https://domainconnect.1and1.com/sync/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain=connect.domains&host=justatest&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo&redirect_uri=http%3A%2F%2Fgoogle.com&state=%7Bname%3Dvalue%7D'), "URL is different than expected"

        # simple test template does not exits
        res = dc.get_domain_connect_template_sync_url("connect.domains", "exampleservice.domainconnect.org",
                                                      "template_not_exists", params={"IP": "132.148.25.185",
                                                                           "RANDOMTEXT": "shm:1531371203:Hejo"})
        print(res)
        assert (res[1] is not None), "There is no error returned and was expected"
        assert (res[0] is None), "There was no url expected"

    def test_get_domain_config(self):
        dc = DomainConnect()
        res, error = dc.get_domain_config('testhost.connect.domains')
        assert (error is None), 'There is an error returned'
        assert (res.domain_root == 'connect.domains'), 'Domain root wrong: {}'.format(res.domain_root)
        assert (res.host == 'testhost'), 'Host not correct: {}'.format(res.host)
        assert (res.urlSyncUX == 'https://domainconnect.1and1.com/sync'), 'urlSyncUX not correct: {}'.format(res.urlSyncUX)
        assert (res.urlAsyncUX == 'https://domainconnect.1and1.com/async'), 'urlAsyncUX not correct: {}'.format(res.urlAsyncUX)
        assert (res.urlAPI == 'https://api.domainconnect.1and1.com'), 'urlAPI not correct: {}'.format(res.urlAPI)
        assert (res.providerName == '1and1'), 'providerName not correct: {}'.format(res.providerName)
        assert (res.uxSize == ('800', '750')), 'uxSize not correct: {}'.format(res.uxSize)

    def test_get_domain_connect_template_async_url(self):
        dc = DomainConnect()

        #simple test sync without host
        res = dc.get_domain_connect_template_async_url("connect.domains", "exampleservice.domainconnect.org", "template2",
                                                       params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                       redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
                                                       state="{name=value}")
        print(res)
        assert(res[1] is None), "There is an error returned"
        assert(res[0] == 'https://domainconnect.1and1.com/async/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                         '?client_id=exampleservice.domainconnect.org&scope=template2&domain=connect.domains'
                         '&host=&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                         '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2Fasync_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res[0])

        #simple test sync with host
        res = dc.get_domain_connect_template_async_url("justatest.connect.domains", "exampleservice.domainconnect.org", "template2",
                                                       params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                       redirect_uri="https://exampleservice.domainconnect.org/async_oauth_response",
                                                       state="{name=value}")
        print(res)
        assert(res[1] is None), "There is an error returned"
        assert(res[0] == 'https://domainconnect.1and1.com/async/v2/domainTemplates/providers/exampleservice.domainconnect.org'
                         '?client_id=exampleservice.domainconnect.org&scope=template2&domain=connect.domains&host=justatest'
                         '&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHejo'
                         '&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2Fasync_oauth_response&state=%7Bname%3Dvalue%7D'), \
            "URL is different than expected: {}".format(res[0])

        # simple test template does not exits
        res = dc.get_domain_connect_template_async_url("connect.domains", "exampleservice.domainconnect.org",
                                                      "template_not_exists", params={"IP": "132.148.25.185",
                                                                           "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                       redirect_uri = "https://exampleservice.domainconnect.org/async_oauth_response")
        print(res)
        assert (res[1] is not None), "There is no error returned and was expected"
        assert (res[0] is None), "There was no url expected"
