import click
import os

@click.command("block")
@click.argument("user")
def entry_point(user):
  CONFIG_DIR  = "~/.passman/"
  CONFIG_FILE = "active"
  print CONFIG_DIR + user
  if os.path.islink(os.path.expanduser(CONFIG_DIR + CONFIG_FILE)) \
      or os.path.isfile(os.path.expanduser(CONFIG_DIR + CONFIG_FILE)):
    os.unlink(os.path.expanduser(CONFIG_DIR + CONFIG_FILE))
  os.symlink(os.path.expanduser(CONFIG_DIR + user), os.path.expanduser(CONFIG_DIR + CONFIG_FILE))