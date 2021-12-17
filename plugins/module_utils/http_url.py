import urllib
from urllib import error as error
import urllib.request
import ssl
import json
from string import Template
import types
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from ..module_utils.http_request import http_get
from requests import HTTPError
import http.client
from requests.structures import CaseInsensitiveDict

"""{
      "hostname": ""
      "port": ""
      "use_certificate": ""
      "api_version": ""
    }
"""
HTTPS="https://"
HTTP= "http://"
API_ASSISTED_INSTALLER = "api.openshift.com/api/assisted-install/"

def create_url(endpoint) -> str: 
    if 'api_version' in endpoint.keys():
        url = str(HTTPS + API_ASSISTED_INSTALLER + endpoint['api_version'])
        return url
    if 'hostname' and 'port' not in endpoint.keys():
       return Exception.with_traceback()
    if 'use_certificate' in endpoint.keys() and endpoint['use_certificate']:
        url = str( HTTPS + endpoint['hostname']+ endpoint['port'] + API_ASSISTED_INSTALLER)
        return url
    else:
        url = str( HTTP + endpoint['hostname']+ endpoint['port'] + API_ASSISTED_INSTALLER)
        return url




    
