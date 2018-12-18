import os.path

def find_config(config):
  #set some default paths to get Passman client configuration
  config_files = [".passmancli", "~/.passman/active", "~/.passman/default"]
  #If there is config override, don't read Passman client configuration
  if config:
    return config
  #Read Passman client configuration
  for config_file in config_files:
    if os.path.isfile(os.path.expanduser(config_file)):
      return config_file
  return None
