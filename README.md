[![Build Status](https://travis-ci.com/Domain-Connect/domainconnect_python.svg?branch=master)](https://travis-ci.com/Domain-Connect/domainconnect_python)

# domain-connect
Python client library for Domain Connect protocol.
For details of the protocol, please visit: https://domainconnect.org

Library offers Service Provider functionality in both Sync and Async mode.

## Specification reference
https://github.com/Domain-Connect/spec/blob/master/Domain%20Connect%20Spec%20Draft.adoc
- Version: 2.1
- Revision: 52


## Usage

### Sync flow

Just get the link. Discovery and template query part is solved automatically.
```python
from domainconnect import *

dc = DomainConnect()

try:
    # change 'connect.domains' to any domain you have access to
    res = dc.get_domain_connect_template_sync_url(domain="foo.connect.domains",
                                                  provider_id="exampleservice.domainconnect.org",
                                                  service_id="template1",
                                                  params={"IP": "132.148.25.185",
                                                          "RANDOMTEXT": "shm:1531371203:Hello world sync"},
                                                  redirect_uri="http://example.com", state="{name=value}")
    print(res)
except DomainConnectException as e:
    print('Exception: {}'.format(e))
    raise
```

Output:
```text
https://domainconnect.1and1.com/sync/v2/domainTemplates/providers/exampleservice.domainconnect.org/services/template1/apply?domain=connect.domains&host=foo&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHello+world+sync&redirect_uri=http%3A%2F%2Fexample.com&state=%7Bname%3Dvalue%7D
```

### Async flow
```python
from domainconnect import *
# to assure input works like raw_input in python 2
from builtins import input

# this will be normally a secret local store on the server
credentials = {
    "1and1": DomainConnectAsyncCredentials(client_id='exampleservice.domainconnect.org',
                                           client_secret='cd$;CVZRj#B8C@o3o8E4v-*k2H7S%)',
                                           api_url='https://api.domainconnect.1and1.com'),
    "GoDaddy": DomainConnectAsyncCredentials(client_id='exampleservice.domainconnect.org',
                                             client_secret='DomainConnectGeheimnisSecretString',
                                             api_url='https://domainconnect.api.godaddy.com'),
}

dc = DomainConnect()

try:
    # change 'connect.domains' to any domain you have access to
    context = dc.get_domain_connect_template_async_context(
        domain='async.connect.domains',
        provider_id='exampleservice.domainconnect.org',
        service_id=['template1', 'template2'], 
        params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hello world async"},
        redirect_uri='https://exampleservice.domainconnect.org/async_oauth_response')
    
    # Route the browser to URL by a link
    print('Please open URL: {}'.format(context.asyncConsentUrl))
    
    # Normally code will arrive as query param on redirect_url
    code = input("Please enter code: ")
    context.code = code
    
    # token will be written into context. Context can be saved and re-used for async calls
    dc.get_async_token(context, credentials[context.config.providerName])
    print('Token obtained')
    
    #apply the template any later with the context
    dc.apply_domain_connect_template_async(
        context, 
        service_id='template1', 
        params={"IP": "132.148.25.185", "RANDOMTEXT": "shm:1531371203:Hello world async"}, 
        force=True)
    print('Template applied')
except DomainConnectException as e:
    print('Exception: {}'.format(e))
    raise

```

Output:
```text
Please open URL: https://domainconnect.1and1.com/async/v2/domainTemplates/providers/exampleservice.domainconnect.org?client_id=exampleservice.domainconnect.org&scope=template1+template2&domain=connect.domains&host=async&IP=132.148.25.185&RANDOMTEXT=shm%3A1531371203%3AHello+world+async&redirect_uri=https%3A%2F%2Fexampleservice.domainconnect.org%2Fasync_oauth_response
Please enter code: >? 8d9a72b5-d2d9-48e3-b615-34fed04d3398
Token obtained
Template applied
```

### Sync flow with signed request

Just get the link. Discovery and template query part is solved automatically.
```python
from domainconnect import *

dc = DomainConnect()

try:
    # change 'connect.domains' to any domain you have access to
    priv_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA18SgvpmeasN4BHkkv0SBjAzIc4grYLjiAXRtNiBUiGUDMeTzQrKTsWvy9NuxU1dIHCZy9o1CrKNg5EzLIZLNyMfI6qiXnM+HMd4byp97zs/3D39Q8iR5poubQcRaGozWx8yQpG0OcVdmEVcTfyR/XSEWC5u16EBNvRnNAOAvZYUdWqVyQvXsjnxQot8KcK0QP8iHpoL/1dbdRy2opRPQ2FdZpovUgknybq/6FkeDtW7uCQ6Mvu4QxcUa3+WP9nYHKtgWip/eFxpeb+qLvcLHf1h0JXtxLVdyy6OLk3f2JRYUX2ZZVDvG3biTpeJz6iRzjGg6MfGxXZHjI8weDjXrJwIDAQABAoIBAGiPedJDwXg9d1i7mCo0OY8z1qPeFh9OGP/Zet8i9bQPN2gjahslTNtK07cDC8C2aFRz8Xw3Ylsk5VxdNobzjFPDNUM6JhawnvR0jQU5GhdTwoc5DHH7aRRjTP6m938sRx0VrfZwfvJAB09Z4jHX7vyjfvprH9EH8GQ2L5lACtfnsSASVJB77H1vtgxTnum74CSqIck1MCjPD/TVUtYfMJwkUQWcbk79N4nvnEoagqsDrvw4okU2OYMWucQjyxfWTU4NGlsDScRbdDAb8sLr3DpMfXM8vpZJ3Ed6gfw14hEJym8XoHwDHmjGmgYH9iG6MODxuO5TLRmRR6b+jcUV/2kCgYEA4WGsDUO/NIXIqtDm5lTi5qeFl0sGKIgRLGuCrvjLF0Fq5Yx28wuow3OhZ3rbjlmhf9nUt24nUUY67plv2pi+vx3kVdbcNfk+Wkc0wfx8+U91qaTplMRhNjrnq/Kp9E7xtnzZRInpUG1Ha5ozTYobVvklUvjodFlF2c16Zz2X2AMCgYEA9RSeZm7oMyJbe985SScXruwt5ZXlUBoBLDZAeMloPpaqknFmSVSNgtniywztF8HppJQyiMvmUOUL2tKnuShXwsvTkCTBC/vNGXutiPS8O2yqeQ8dHoHuKcoMFwgajrbPrVkuFtUkjbQJ/TKoZtrxUdCryDZ/AHmRtiHh9E4NUQ0CgYAE7ngvSh4y7gJ4Cl4jCBR26492wgN+e4u0px2S6oq3FY1bPHmV09l7fVo4w21ubfOksoV/BgACPUEo216hL9psoCDQ6ASlgbCllQ1IeVfatKxka+FYift+jkdnccXaPKf5UD4Iy+O5CMsZRaR9u9nhS05PxHaBpTpsC5z0CVr7NQKBgQCsBTzpSQ9SVNtBpvzei8Hj1YKhkwTRpG8OSUYXgcbZp4cyIsZY0jBBmA3H19rSwhjsm9icjAGs5hfcD+AJ5nczEz37/tBBSQw8xsKXTrCQRUWikyktMKWqT1cNE3MQmOBMHDxtak2t6KDaR6RMDYE0m/L3JMkf3DSaUk323JIcQQKBgD6lHhw79Cenpezzf0566uWE1QF6Sv3kWk6Gkzo2jUGmjo2tG1v2Nj82DvcTuqvfUKSr2wTKINxnKGyYXGto0BykdxeFbR04cNcBB46zUjasro2ZCvIoAHCpohNBI2dL6dI+RI3jC/KY3jPNI0toaOTWkeAvJ7w09G2ttlv8qLNV\n-----END RSA PRIVATE KEY-----'
    res = dc.get_domain_connect_template_sync_url(domain="signed.connect.domains",
                                                  provider_id="exampleservice.domainconnect.org",
                                                  service_id="template2",
                                                  params={"IP": "132.148.25.185",
                                                          "RANDOMTEXT": "shm:1531371203:Hejo"},
                                                  sign=True,
                                                  private_key=priv_key,
                                                  keyid='_dck1')
    print(res)
except DomainConnectException as e:
    print('Exception: {}'.format(e))
    raise
```

## Custom http/https proxy or dns resolver

```python
from domainconnect import *

dc = DomainConnect(
    networkcontext=NetworkContext(
        proxy_host='proxy.host', 
        proxy_port='proxy.port', 
        nameservers='resolver.host')
    )
```

## TODOs
- support for provider_name (for shared templates)
- async revert

## CHANGELOG
| version | date       | changes                                                                         |
|---------|------------|---------------------------------------------------------------------------------|
| 0.0.11  | 2024-02-18 | DEPENDENCIES: updated cryptography to the highest one for newer python versions |
| 0.0.10  | 2024-02-18 | DEPENDENCIES: updated cryptography for newer python versions                    |
| 0.0.9   | 2021-04-13 | NEW FEATURE: support for openwrt (missing webbrowser module)                    |
| 0.0.8   | 2020-11-09 | NEW FEATURE: Detailed information on access token request fail                  |
| 0.0.7   | 2019-10-29 | Bugfix: error when setting up .app domain                                       |
| 0.0.6   | 2019-07-05 | UPDATE: moved from pycrypto to cryptography (due to know security issues)       |
| 0.0.5   | 2019-03-12 | NEW FEATURE: url signing capability added                                       |
