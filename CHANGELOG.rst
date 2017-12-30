.. :changelog:

Changelog for passmancli
------------------------

0.2.2 (Danh Huynh)
++++++++++++++++++

* Add CLI option to delete credential by guid
* Fix: shared credential use different key to decrypt ciphertext
* Refactor and cleanup codes
* Enable credential CLI option (new and update).
* Create new credential works using the cread_cred.json template


0.2.1 (Danh Huynh)
++++++++++++++++++

* Add option to filter the credential result by list of comma separated keys
* Add option to search and get selected credentials in the target vault
* Remove unimplemented credential CLI options (new and update)

0.2.0 (Danh Huynh)
++++++++++++++++++

* Decrypt vault and credentials successfully.
* Change default config file to .passmancli or ~/.config/.passmancli
* Hide some unwanted fields in the result for better visual
* Hide test key for vault in the result
* Hide deleted credentials in the result
* Fix epoch time display in get vault
* Cleaning up and styling


0.1.0 (Danh Huynh)
++++++++++++++++++

* Folking from Douglas's original work
* Replace TOML config lib by ConfigParser lib
* Add JSON format and highlight to the responses
* Show datetime instead of epoch time
* Allow to get vault by name along with guid
* Update mechanism to get key and decrypt the credentials (work in progress)


0.0.1 (Douglas Camata)
++++++++++++++++++++++

* On the works
