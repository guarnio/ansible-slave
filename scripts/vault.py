DOCUMENTATION = """
        lookup: file
        author: Marco Guarnieri <mguarnieri@outlook.es>
        version_added: "0.0.2"
        short_description: read hashicorp vault secrets
        description:
            - This lookup returns the specified secret from a hashicorp vault server, on a default Ansible installation on RHEL 8.x copy current file on /usr/share/ansible/plugins/lookup (or locally on ~/.ansible/plugins/lookup/vault.py) directory.
        options:
          _terms:
            url: vault url imported from VAULT_ADDR env variable
            role_id: approle role id imported from VAULT_ROLE_ID env variable
            secret_id: approle secret id imported from VAULT_SECRET_ID env variable
            tmp_key: secret path (without "secret/data/")
            field: key=value filed to return
        notes:
          - tested with Ansible 2.11.2 on Fedora 34 and macOS Monterey
"""

 # Plugin usage example:
 #
 # ldap_certificate: "{{ lookup('vault', 'secret/rhds/certificates', 'cert', None, None, 'token', None, None, None) }}"

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import requests
import os
import urllib3
import json

from urllib.parse import urljoin

display = Display()

class LookupModule(LookupBase):

  def gen_token(self):
      data = {
              'role_id': self.role_id,
              'secret_id': self.secret_id
              }

      data2 = json.dumps(data)
      display.v("pre request")
      url_request = requests.post(self.url + "/v1/auth/approle/login" , data = data2, verify=False)
      display.v("post request")
      petition = json.loads(url_request.content)
      return petition["auth"]["client_token"]

  def get_mount_version(self):
      mounts_route = "sys/mounts"
      request_url = urljoin(self.url, "v1/%s" % (mounts_route))
      headers = { 'X-Vault-Token' : "root" }
      mount_request =  (requests.get(request_url, headers=headers, verify=False, stream=True))
      mount_json =  json.loads(mount_request.content)
      mount_version =  (mount_json['secret/']['options']['version'])
      return mount_version

  def read_secret(self):
      mount_version = "2"

      if mount_version == "2":
        if self.secret_path.find('secret/data') != -1:
          key_final=self.secret_path
        else:
          key_final='secret/data/' + self.secret_path

      request_url = urljoin(self.url, "v1/%s" % (key_final))
      headers = { 'X-Vault-Token' : self.token }
      display.v("pre try")

      result_raw = requests.get(request_url, headers=headers, verify=False, stream=True)
      result = json.loads(result_raw.content)
      if result_raw.status_code == 404:
        display.v("secret does not exists")
        raise ValueError('secret does not exists')

      if self.authMethod == 'userpass' or self.authMethod == 'app-id':
              headers = { 'X-Vault-Token' : self.token }
              response = api_call(urljoin(self.url, "v1/auth/token/revoke-self"), '', headers)
              if response.code != 204:
                  raise AnsibleError('Unable to revoke token.')
      if mount_version == "2" :
              return [result['data']['data'][self.key]] if self.key is not None else [result['data']['data']]
      elif mount_version == "1":
              return [result['data'][self.key]] if self.key is not None else [result['data']]

  def run(self, terms, variables=None, **kwargs):
      self.url=os.environ['VAULT_ADDR']
      self.role_id=os.environ['VAULT_ROLE_ID']
      self.secret_id=os.environ['VAULT_SECRET_ID']
      ret = []
      urllib3.disable_warnings()
      #self.url=terms[2]
      #self.role_id=terms[3]
      #self.secret_id=terms[4]
      self.secret_path=terms[0]

      self.token=self.gen_token()
      self.authMethod="approle"
      if terms[0].split('/')[0] != 'secret':
        self.secret_path=terms[0]
      else:
        self.secret_path=terms[0].split('/',1)[1]
      self.key=terms[1]

      ret=self.read_secret()
      return ret