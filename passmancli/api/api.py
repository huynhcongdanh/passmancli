import json
import requests
import time

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

import base64
from sjcl import SJCL


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PassmanApi(object):

  ENCRYPTED_VAULT_FIELDS = [u"description", u"username", u"password", u"otp", u"files",
                            u"custom_fields", u"email", u"tags", u"url"]
  JSON_FIELDS            = [u"tags", u"custom_fields"]
  DATE_FIELDS            = [u"created", u"last_access", u"changed", u"expire_time",
                            u"delete_time", u"sharing_keys_generated"]
  UNWANTED_FIELDS        = [u"vault_settings", u"public_sharing_key", u"private_sharing_key",
                            u"icon", u"delete_time", u"hidden", u"vault_id", u"renew_interval",
                            u"otp", u"credential_id", u"challenge_password"]
  SEARCH_FIELDS          = [u"label", u"tags", u"username", u"description", u"email", u"url"]

  DEFAULT_FIELDS         = [u"label"]

  def __init__(self, base_url, user, password, vault_password):
    self.base_url       = base_url
    self.user           = user
    self.password       = password
    self.vault_password = vault_password
    self._auth_headers = {
      "Authorization": "Basic {}".format(
        base64.b64encode(self.user + ":" + self.password)
      )
    }

  def _send_request(self, verb, endpoint, data=None):
    return getattr(requests, verb)(
      self.base_url + endpoint,
      headers=self._auth_headers,
      data=data,
      verify=False
    )

  def get_vaults(self):
    #get raw response
    vaults      = self._get_vaults()
    #convert epoch time
    self._format_vault_time(vaults)
    #remove/hide unwanted fields
    for vault in vaults:
      for field, value in vault.items():
        if field in self.UNWANTED_FIELDS:
          del vault[field]
        if "delete_request_pending" in field and not value:
          del vault[field]
    #format json response
    json_vaults = json.dumps(vaults, indent=2, sort_keys=True)
    response = highlight(json_vaults, JsonLexer(), TerminalFormatter())
    return response

  def _get_vaults(self):
    endpoint = "v2/vaults"
    #get raw response
    return self._send_request("get", endpoint).json()

  def _get_vault_guid(self, input):
    vaults = self._get_vaults()
    #by the default, let guid be user input
    guid   = input
    #check the user input and get guid if matches
    for vault in vaults:
      for field, value in vault.iteritems():
        if field == "name" and value == input:
          guid = vault["guid"]
    return guid

  def _get_cred_guids(self, vault, input):
    endpoint = "v2/vaults/{}".format(self._get_vault_guid(vault))
    current_vault = self._send_request("get", endpoint).json()
    guid_list   = []
    #check the user input and get guid if matches
    for credential in current_vault["credentials"]:
      for field, value in credential.items():
        if field in self.SEARCH_FIELDS and input.lower() in value.lower() and credential["delete_time"] == 0:
          guid_list.append(credential["guid"])
          break
    return guid_list

  def get_vault(self, guid):
    endpoint = "v2/vaults/{}".format(self._get_vault_guid(guid))
    #get raw response
    vault = self._send_request("get", endpoint).json()
    #remove/hide test key for vault
    self._remove_test_key(vault)
    #remove/hide deleted credential from the response
    self._remove_deleted_creds(vault)
    #convert epoch time
    self._format_cred_time(vault)
    #remove/hide unwanted fields
    self._remove_unwanted_fields(vault)
    #decrypt values
    self._get_decrypted_response(vault, self.vault_password)
    #format json response
    json_vault = json.dumps(vault, indent=2, sort_keys=False)
    response = highlight(json_vault, JsonLexer(), TerminalFormatter())
    return response

  def get_credential(self, vault, guid, keys):
    cred_list = []
    guid_list = self._get_cred_guids(vault, guid)
    if guid_list:
      for guid in guid_list:
        endpoint = "v2/credentials/{}".format(guid)
        cred     = self._send_request("get", endpoint).json()
        #cleanup and decrypt creds
        for field, value in cred.items():
          if keys != None and field not in keys.split(',') and field not in self.DEFAULT_FIELDS:
            del cred[field]
          elif field in self.UNWANTED_FIELDS:
            del cred[field]
          elif field in self.DATE_FIELDS and value != 0:
            cred[field] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value)))
          elif field in self.ENCRYPTED_VAULT_FIELDS:
            text = self._get_decrypted_text(value, self.vault_password)
            if field in self.JSON_FIELDS:
              text = json.loads(text)
            cred[field] = text
        cred_list.append(cred)
    #format json response
    cred_list = json.dumps(cred_list, indent=4, sort_keys=False)
    cred_list = highlight(cred_list, JsonLexer(), TerminalFormatter())
    return cred_list

  def _format_vault_time(self, vaults):
    for vault in vaults:
      vault.update((field, time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value))))
                   for field, value in vault.iteritems() if field in self.DATE_FIELDS)

  def _format_cred_time(self, vault):
    #update current vault
    for field, value in vault.items():
      if field in self.DATE_FIELDS and value != 0:
          vault[field] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value)))
    #update creds
    for credential in vault["credentials"]:
      for field, value in credential.items():
        if field in self.DATE_FIELDS and value != 0:
            credential[field] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value)))

  def _remove_test_key(self,vault):
    vault["credentials"] = [credential for credential in vault["credentials"]
                            if "Test key for vault" not in credential["label"]]

  def _remove_unwanted_fields(self, vault):
    for field, value in vault.items():
      if field in self.UNWANTED_FIELDS:
        del vault[field]
      if "delete_request_pending" in field and not value:
        del vault[field]
    for credential in vault["credentials"]:
      for field, value in credential.items():
        if field in self.UNWANTED_FIELDS:
          del credential[field]

  def _remove_deleted_creds(self, vault):
    vault["credentials"] = [c for c in vault["credentials"] if c["delete_time"] == 0]

  def _get_decrypted_response(self, vault, vault_password):
    for credential in vault["credentials"]:
      for field, value in credential.items():
        if field in self.ENCRYPTED_VAULT_FIELDS:
          text = self._get_decrypted_text(value, vault_password)
          if field in self.JSON_FIELDS:
            text = json.loads(text)
          credential[field] = text

  def _get_decrypted_text(self, ciphertext, key):
    data = eval(base64.b64decode(ciphertext))
    return SJCL().decrypt(data, key).strip('"')

  def new_credential(self, **data):
    endpoint = "v2/credentials"
    response = self._send_request("post", endpoint, data=data).json()
    return response

  def update_credential(self, **data):
    endpoint = "v2/credentials"
    response = self._send_request("patch", endpoint, data=data).json()
    return response
