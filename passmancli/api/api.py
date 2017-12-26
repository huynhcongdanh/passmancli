import json
import requests
import time

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

import base64
import hmac,hashlib
from sjcl import SJCL


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PassmanApi(object):

  ENCRYPTED_VAULT_FIELDS = [u"description", u"username", u"password", u"files",
                            u"custom_fields", u"otp", u"email", u"tags", u"url"]
  DATE_FIELDS = [u"created", u"last_access", u"changed", u"expire_time", u"delete_time"]

  def __init__(self, base_url, server_key, auth):
    self.base_url = base_url
    self.server_key = server_key
    self.auth = auth
    self._auth_headers = {
      "Authorization": "Basic {}".format(
        base64.b64encode(":".join(auth))
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
    raw      = self._get_vaults()
    #convert epoch time
    self._format_vault_time(raw)
    #format json response
    json_raw = json.dumps(raw, indent=4, sort_keys=False)
    response = highlight(json_raw, JsonLexer(), TerminalFormatter())
    return response

  def _get_vaults(self):
    endpoint = "v2/vaults"
    #get raw response
    return self._send_request("get", endpoint).json()

  def _get_vault_guid(self,input):
    vaults = self._get_vaults()
    #by the default, let guid be user input
    guid   = input
    #check the user input and get guid if matches
    for vault in vaults:
      for k, v in vault.iteritems():
        if k == "name" and v == input:
          guid = vault["guid"]
    return guid

  def get_vault(self, guid, decrypt=False, key=None):
    endpoint = "v2/vaults/{}".format(self._get_vault_guid(guid))
    #get raw response
    raw = self._send_request("get", endpoint).json()
    #remove/hide deleted credential from the response
    self._remove_deleted_creds(raw)
    #convert epoch time
    self._format_cred_time(raw)
    #decrypt values
    if decrypt and key:
      self._get_decrypted_response(raw)

    #format json response
    json_raw = json.dumps(raw, indent=4, sort_keys=False)
    response = highlight(json_raw, JsonLexer(), TerminalFormatter())
    return response

  def _format_vault_time(self, response):
    for vault in response:
      vault.update((k, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(v))))
                   for k, v in vault.iteritems() if k in self.DATE_FIELDS)

  def _format_cred_time(self, response):
    #update current vault
    for field, value in response.items():
      if field in self.DATE_FIELDS:
        if value != 0:
          response[field] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(value)))
    #update creds
    for credential in response["credentials"]:
      for field, value in credential.items():
        if field in self.DATE_FIELDS:
          if value != 0:
            credential[field] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(value)))

  def _remove_deleted_creds(self,response):
    response["credentials"] = [c for c in response["credentials"] if c['delete_time'] == 0]

  def _get_decrypted_response(self, response):
    for credential in response["credentials"]:
      for field, value in credential.items():
        if field in self.ENCRYPTED_VAULT_FIELDS:
          #get key to decrypt
          key = self._get_key_from_cred(credential)
          credential[field] = self._get_decrypted_cred(value,key)

  def _get_key_from_cred(self,credential):
    user_shared_key    = credential["shared_key"]
    user_supplied_key  = str(credential["label"]).encode("utf-8")
    user_key           = str(credential["user_id"]).encode("utf-8")
    server_key         = self.server_key.encode("utf-8")
    if user_shared_key is not None:
      user_key = str(user_shared_key).encode("utf-8")
    key = hmac.new(server_key, user_key, hashlib.sha512).hexdigest()
    key = hmac.new(user_supplied_key, key, hashlib.sha512).hexdigest()
    return key

  def _get_decrypted_cred(self,ciphertext, key):
    print key
    print ciphertext
    data = eval(base64.b64decode(ciphertext.encode("utf-8")))
    print data
    return SJCL().decrypt(data)

  def new_credential(self, **data):
    endpoint = "v2/credentials"
    response = self._send_request("post", endpoint, data=data).json()
    return response

  def update_credential(self, **data):
    endpoint = "v2/credentials"
    response = self._send_request("patch", endpoint, data=data).json()
    return response


class Credential(object):
  def __init__(self, guid, vaultId, userId, label, description, created, changed, tags, email, username, password, url,
               favicon, renewInterval, expireTime, deleteTime, files, customFields, otp, hidden, sharedKey):
    self.guid = guid
    self.vaultId = vaultId
    self.userId=  userId
    self.label = label
    self.description = description
    self.created = created
    self.changed = changed
    self.tags = tags
    self.email = email
    self.username = username
    self.password = password
    self.url = url
    self.favicon=  favicon
    self.renewInterval = renewInterval
    self.expireTime = expireTime
    self.deleteTime = deleteTime
    self.files=  files
    self.customFields = customFields
    self.otp = otp
    self.hidden = hidden
    self.sharedKey = sharedKey