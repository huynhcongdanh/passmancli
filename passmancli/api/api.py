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
  JSON_FIELDS            = [u"tags", u"custom_fields", u"files"]
  DATE_FIELDS            = [u"created", u"last_access", u"changed", u"expire_time",
                            u"delete_time", u"sharing_keys_generated"]
  UNWANTED_FIELDS        = [u"vault_settings", u"public_sharing_key", u"private_sharing_key",
                            u"icon", u"favicon", u"delete_time", u"hidden", u"renew_interval",
                            u"otp", u"credential_id", u"challenge_password"]
  SEARCH_FIELDS          = [u"label", u"tags", u"username", u"description", u"email", u"url"]
  DEFAULT_FIELDS         = [u"label"]

  def __init__(self, base_url, user, password, vault_password):
    self.base_url       = base_url
    self.user           = user
    self.password       = password
    self.vault_password = vault_password
    self._auth_headers  = {
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
    for vault in vaults:
      vault.update((field, time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value))))
                   for field, value in vault.iteritems() if field in self.DATE_FIELDS)
    #remove/hide unwanted fields
    for vault in vaults:
      for field, value in vault.items():
        if field in self.UNWANTED_FIELDS:
          del vault[field]
        if "delete_request_pending" in field and not value:
          del vault[field]
    vaults = self._format_json(vaults)
    return vaults

  def get_vault(self, guid, keys):
    guid = self._get_vault_guid(guid)
    if guid:
      endpoint = "v2/vaults/{}".format(guid)
      #get raw response
      vault = self._send_request("get", endpoint).json()
      #remove/hide test key for vault
      vault["credentials"] = [cred for cred in vault["credentials"]
                              if "Test key for vault" not in cred["label"]]
      #remove/hide deleted credential from the response
      vault["credentials"] = [c for c in vault["credentials"] if c["delete_time"] == 0]

      #convert epoch time
      for field, value in vault.items():
        if field in self.DATE_FIELDS and value != 0:
          vault[field] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value)))
      #remove/hide unwanted fields
      for field, value in vault.items():
        if field in self.UNWANTED_FIELDS:
          del vault[field]
        if "delete_request_pending" in field and not value:
          del vault[field]
      for cred in vault["credentials"]:
        self._format_cred_time(cred)
        self._clean_cred(cred, keys)
      #decrypt values
      self._get_decrypted_response(vault)
      #format json response
      vault = self._format_json(vault)
      return vault
    else:
      return "Vault not found!"

  def get_credential(self, vault, guid, keys):
    guid_list = self._get_cred_guids(vault, guid)
    if guid_list:
      cred_list = []
      for guid in guid_list:
        endpoint = "v2/credentials/{}".format(guid)
        cred     = self._send_request("get", endpoint).json()
        self._clean_cred(cred, keys)
        self._format_cred_time(cred)
        self._get_decrypted_cred(cred)
        cred_list.append(cred)
      cred_list = self._format_json(cred_list)
      return cred_list
    else:
      return "Credential not found!"

  def new_credential(self, data):
    endpoint = "v2/credentials"
    cred = self._send_request("post", endpoint, data=json.loads(open(data).read())).json()
    return self._format_json(cred)

  def update_credential(self, guid, data):
    endpoint = "v2/credentials/{}".format(guid)
    cred = self._send_request("patch", endpoint, data=json.loads(open(data).read())).json()
    return self._format_json(cred)

  def _get_vaults(self):
    endpoint = "v2/vaults"
    return self._send_request("get", endpoint).json()

  def _get_vault_guid(self, input):
    guid = None
    #check the user input and get guid if matches
    for vault in self._get_vaults():
      for field, value in vault.iteritems():
        if field == "guid" and value == input:
          guid = vault["guid"]
        elif field == "name" and value == input:
          guid = vault["guid"]
    return guid

  def _get_cred_guids(self, vault, input):
    vault_guid = self._get_vault_guid(vault)
    if vault_guid:
      endpoint = "v2/vaults/{}".format(vault_guid)
      current_vault = self._send_request("get", endpoint).json()
      guid_list   = []
      #check the user input and get guid if matches
      for cred in current_vault["credentials"]:
        for field, value in cred.items():
          if field in self.SEARCH_FIELDS and input.lower() in value.lower() and cred["delete_time"] == 0:
            guid_list.append(cred["guid"])
            break
      return guid_list
    else:
      return None

  def _clean_cred(self, cred, keys):
    for field, value in cred.items():
      if keys != None and field not in keys.split(',') and field not in self.DEFAULT_FIELDS:
        del cred[field]
      elif field in self.UNWANTED_FIELDS:
        del cred[field]

  def _format_cred_time(self, cred):
    for field, value in cred.items():
      if field in self.DATE_FIELDS and value != 0:
        cred[field] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.localtime(int(value)))

  def _format_json(self, json_data):
    json_data = json.dumps(json_data, indent=4, sort_keys=False)
    json_data = highlight(json_data, JsonLexer(), TerminalFormatter())
    return json_data

  def _get_decrypted_response(self, vault):
    for cred in vault["credentials"]:
      self._get_decrypted_cred(cred)

  def _get_decrypted_cred(self, cred):
    if not cred["shared_key"]:
      for field, value in cred.items():
        if field in self.ENCRYPTED_VAULT_FIELDS:
          text = self._get_decrypted_text(value, self.vault_password)
          if field in self.JSON_FIELDS:
            text = json.loads(text)
          cred[field] = text
    else:
      shared_key = self._get_decrypted_text(cred["shared_key"], self.vault_password)
      cred["shared_key"] = shared_key
      for field, value in cred.items():
        if field in self.ENCRYPTED_VAULT_FIELDS:
          text = self._get_decrypted_text(value, shared_key)
          if field in self.JSON_FIELDS:
            text = json.loads(text)
          cred[field] = text

  def _get_decrypted_text(self, ciphertext, key):
    data = eval(base64.b64decode(ciphertext))
    return SJCL().decrypt(data, key).strip('"')