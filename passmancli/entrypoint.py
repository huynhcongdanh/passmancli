import click
import ConfigParser
import os

from passmancli.cli import block, vault, cred
from passmancli.api import PassmanApi
from passmancli.config import find_config

#Create CLI options
@click.group()
@click.option("--config", "-c", type=click.Path(),  help="Path to Passman client config file")
@click.option("--vault_password", "-p", required=False, help="Specify vault password if different than login password")
@click.version_option(version=None)
@click.pass_context

#Config entrypoint for CLI
def entrypoint(ctx, config, vault_password):
  #check if config file is found or specified
  config_file = find_config(config)
  if config_file:
    cfg = ConfigParser.RawConfigParser()
    try:
      cfg.read(os.path.expanduser(config_file))
    except Exception as e :
      print(str(e))
    try:
      base_url     = cfg.get('passman', 'base_url')
      user         = cfg.get('passman', 'user')
      password     = cfg.get('passman', 'password')
    except Exception as e :
      print(str(e),' could not read configuration file or missing values')
    #check if vault password is specified
    if not vault_password:
      vault_password = password
    #load the configs
    ctx.obj["passman"] = PassmanApi(base_url, user, password, vault_password)
  else:
    print('Passman configuration file is not found or specified')

def main():
  entrypoint.add_command(block.entry_point)
  entrypoint.add_command(vault.entry_point)
  entrypoint.add_command(cred.entry_point)
  entrypoint(obj={})


if __name__ == '__main__':
  main()
