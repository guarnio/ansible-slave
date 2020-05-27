# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
        lookup: file
        author: Marco Guarnieri <mguarnieri@outlook.es>
        version_added: "0.0.1"
        short_description: read hashicorp vault secrets
        description:
            - This lookup returns the specified secret from a hashicorp vault server, on a default Ansible installation on RHEL 8.x copy current file on /usr/share/ansible/plugins/lookup directory.
        options:
          _terms:
            url: vault url
            role_id: approle role id
            secret_id: approle secret id
            tmp_key: secret path (without "secret/data/")
            field: key=value filed to return
        notes:
          - tested with Ansible 2.9.6 on RHEL 8.1
"""

 # Plugin usage example:
 #
 # ldap_certificate: "{{ lookup('vault', 'rhds/certificates', 'cert', vault_server, vault_role_id, vault_secret_it) }}"

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import requests
import os
import urllib3
import re
import json
import sys

import urllib.parse as urlparse
from urllib.parse import urljoin
import urllib.request

def gen_token(url,role_id,secret_id):
    data = {
            'role_id': role_id,
            'secret_id': secret_id
            }

    data2 = json.dumps(data)
    url_request = requests.post(url + "/v1/auth/approle/login" , data = data2, verify=False)
    petition = json.loads(url_request.content)
    return petition["auth"]["client_token"]

def get_mount_version(url,token):
    mounts_route = "sys/mounts"
    request_url = urljoin(url, "v1/%s" % (mounts_route))
    headers = { 'X-Vault-Token' : token }
    mount_request =  (requests.get(request_url, headers=headers, verify=False, stream=True))
    mount_json =  json.loads(mount_request.content)
    mount_version =  (mount_json['secret/']['options']['version'])
    return mount_version

def read_secret(url,tmp_key,token,authMethod,field):
    mount_version = get_mount_version(url,token)

    if mount_version == "2":
      if tmp_key.find('secret/data') != -1:
        key=tmp_key
      else:
        key='secret/data/' + tmp_key

    request_url = urljoin(url, "v1/%s" % (key))
    headers = { 'X-Vault-Token' : token }

    result_raw = (requests.get(request_url, headers=headers, verify=False, stream=True))
    result = json.loads(result_raw.content)

    if authMethod == 'userpass' or authMethod == 'app-id':
            headers = { 'X-Vault-Token' : token }
            response = api_call(urljoin(url, "v1/auth/token/revoke-self"), '', headers)
            if response.code != 204:
                raise AnsibleError('Unable to revoke token.')
    if mount_version == "2" :
            return [result['data']['data'][field]] if field is not None else [result['data']['data']]
    elif mount_version == "1":
            return [result['data'][field]] if field is not None else [result['data']]

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []
        urllib3.disable_warnings()
        url=terms[2]
        roleid=terms[3]
        secretid=terms[4]
        secret_path=terms[0]
        key=terms[1]

        ret=read_secret(url,secret_path,gen_token(url,roleid,secretid),"approle",key)
        return ret
