import urllib
from urllib import error as error
import urllib.request
import ssl
import json
from string import Template
import types
from ansible.module_utils.basic import AnsibleModule
#from module_utils.init.http_request import http_post, http_request
from ansible.module_utils._text import to_text
from ansible.module_utils.urls import open_url
from ..module_utils.http_request import __http_request
from requests import HTTPError
import http.client
from requests.structures import CaseInsensitiveDict


def __api_call(module):
        base_url=module.params.get('url_endpoint')
        data=module.params.get('body')
        method=module.params.get('method')
        auth=module.params.get('auth')
        access_token=module.params.get('auth')
        query=module.params.get('query')
        url = str(base_url)
        reply = query
#       epoch = module.params.get("epoch")
        response = __http_request(method, url, auth, access_token, reply, data=data)
        try:
            
            response ={ query: response[query] } 
            module.exit_json(changed=True,json=response)
        except Exception as e:
                        module.fail_json(
                            msg="Error, token is invalid or error in request "
                        )
     
    
def main():
    

    fields = dict(
        body=dict(required=True, type='dict'),
        method=dict(required=True, type='str'),
        auth=dict(required=True, type='dict'),
        url_endpoint=dict(required=True, type='dict'),

        query=dict(required=True,type='str'),
    )
    required_together = [["auth", "url_endpoint"]]

    #module parameter
    module = AnsibleModule(
        argument_spec=fields,
        required_together=required_together,
        supports_check_mode=True
    )
    (changed, json) = __api_call(module)
    


    module.exit_json(changed=changed, json=json)
if __name__ == '__main__':

    main()

