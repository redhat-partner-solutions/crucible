from os import access, error
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
import json
import os
import datetime
import requests
import http.client
from requests.structures import CaseInsensitiveDict
from ansible.parsing.vault import *
from ansible.constants import DEFAULT_VAULT_ID_MATCH
def refresh_token(auth):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    url = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
    data = {"grant_type":"refresh_token", "client_id": "cloud-services", "refresh_token": auth['api_token']}
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    if response.status_code == 200 or 201:
            refresh_auth = {}
            refresh_auth['api_token'] = auth['api_token']
            refresh_auth['access_token'] = response.json()['access_token']
            refresh_auth['expires_in'] = response.json()['expires_in']
            return refresh_auth

    else:
        return 401


def restore_token(auth) -> dict:
    api_token = auth['api_token']
    secret = api_token.encode('utf-8')
    file_name = "/tmp/ocm_auth.yml"
    try:
        encrypted_data = open(file_name, 'r').read()
        decrypted_data = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))]).decrypt(encrypted_data)
        auth = json.loads(decrypted_data)
    except json.JSONDecodeError:
        return auth
    except FileNotFoundError:
        return auth
    return auth
    
def store_token(auth):
    api_token = auth['api_token']
    secret = api_token.encode('utf-8')
    vault = VaultLib(secrets=VaultSecret(secret))
    file_name = "/tmp/ocm_auth.yml"
    try:
        file = open(file_name, 'w')
    except FileNotFoundError:
        file = open(file_name, 'x')
    to_string = json.dumps(auth)
    file.write(to_string) 
    file.close()
    VaultEditor(vault=vault).encrypt_file(filename=file_name,secret=vault.secrets)

    return None
