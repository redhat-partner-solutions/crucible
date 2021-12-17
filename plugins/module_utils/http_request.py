import json
import requests
import base64 
from requests.models import HTTPError
from ..module_utils.http_token import refresh_token, store_token, restore_token
## Constants:
SUCCESS_CODES = {200, 201}
AUTH_FAILURE_CODES = {401, 500}
########################### Helper methods/Primative ###################################
# exi
# This section contains helper methods for Assisted Installer
#
################################################################################

def http_get(url, auth, reply, data):
    return _http_request(requests.get, "GET", url, auth, reply, data)
    
def http_get(url, auth, reply, data):
    return _http_request(requests.get, "GET", url, auth, reply, data)


def http_post(url, auth, reply, data):
    return _http_request(requests.post, "POST", url, auth, reply, data)

def http_download(url, auth, reply, data):
    return _get_url(url, auth, reply, data)

def http_put( url, auth, reply, data):
    return _http_request(requests.put, "PUT", url, auth, reply, data)


def http_patch( url, auth, reply, data):
    return _http_request(requests.patch, "PATCH",  url, auth, reply, data)


def http_delete( url, auth, reply, data):
    return _http_request(requests.delete, "DELETE",  url, auth, reply, data)

def _get_auth_header(auth):
    #TODO basic authentication
    #auth = {'access_token':'', 'api_token':''}
    if 'access_token' in auth.keys():
        return requests.structures.CaseInsensitiveDict(
            {
                "Authorization": "Bearer {0}".format(auth['access_token']),
                "Content-Type": "application/json",
            }
        )
    if 'username' and 'password' in auth.keys():
        authorization = str(auth['username'] + ":" + auth['password']).encode('ascii')
        return requests.structures.CaseInsensitiveDict(
            {
                "Authorization": "Basic " + str(base64.b64encode(authorization))
            }
        )
    else:
        return None
class UnhandledStatusCode(Exception):
    pass



def _http_request(request_handler, method, url, auth, reply, data, retries=3):
    if retries == 0:
        return requests.exceptions.TooManyRedirects

    request_data = json.dumps(data)

    if 'api_token' in auth.keys():
        auth = restore_token(auth)
    
    response = request_handler(url, headers=_get_auth_header(auth), data=request_data)
    try:
        response.raise_for_status()
        
    except requests.exceptions.HTTPError:
        status = response.status_code
        if status in AUTH_FAILURE_CODES:
            if 'api_token' in auth.keys():
                refresh_auth = refresh_token(auth) 
                store_token(refresh_auth)
                return _http_request(request_handler, method, url, refresh_auth, reply, data, retries-1)

    return response.json()

def _get_url(url, auth, reply, data, retries=3):
    if retries == 0:
        return requests.exceptions.TooManyRedirects

    request_data = json.dumps(data)

    if 'api_token' in auth.keys():
        auth = restore_token(auth)
    
    response = requests.get(url, headers=_get_auth_header(auth),stream=True, allow_redirects=True)
    try:
        response.raise_for_status()
        with open('/tmp/discovery.iso', 'wb') as f:
            f.write(response.content)
            f.close()
    except requests.exceptions.HTTPError:
        status = response.status_code
        if status in AUTH_FAILURE_CODES:
            if 'api_token' in auth.keys():
                refresh_auth = refresh_token(auth) 
                store_token(refresh_auth)
                return _get_url(url, refresh_auth, reply, data, retries-1)

    return "Download Successful"
