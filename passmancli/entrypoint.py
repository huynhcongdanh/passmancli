import click
import ConfigParser
import os

from passmancli.cli import vault, credential
from passmancli.api import PassmanApi
from passmancli.config import find_config

#Create CLI options
@click.group()
@click.option("--config", "-c", type=click.Path(),  help="Path to Passman client config file")
@click.version_option(version=None)
@click.pass_context

#Config entrypoint for CLI
def entrypoint(ctx, config):
  #check if config file is found or specified
  config_file = find_config(config)
  if config_file:
    cfg = ConfigParser.RawConfigParser()
    try:
      cfg.read(os.path.expanduser(config_file))
    except Exception as e :
      print(str(e))
    try:
      base_url   = cfg.get('passman', 'base_url')
      server_key = cfg.get('passman', 'server_key')
      user       = cfg.get('passman', 'user')
      password   = cfg.get('passman', 'password')
    except Exception as e :
      print(str(e),' could not read configuration file')
    #load the configs
    ctx.obj["passman"] = PassmanApi(base_url, server_key, (user, password))
  else:
    print('Passman configuration file is not found or specified')

def main():
  entrypoint.add_command(vault.entry_point)
  entrypoint.add_command(credential.entry_point)
  entrypoint(obj={})


if __name__ == '__main__':
  main()
