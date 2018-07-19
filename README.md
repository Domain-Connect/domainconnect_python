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
- serialization and deserialization of context for easy storage 
- support for signatures
- support for provider_name (for shared templates)
- check of async access_token validity and refresh
- async revert