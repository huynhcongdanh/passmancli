import click


@click.group("vault")
@click.pass_context
def entry_point(ctx):
  pass

@entry_point.command("list")
@click.pass_context
def get_vaults(ctx):
  print ctx.obj["passman"].get_vaults()

@entry_point.command("show")
@click.argument("guid")
@click.option("--keys", "-k", required=False, help="Filter the result by list of comma separated keys")
@click.pass_context
def get_vault(ctx, guid, keys):
  print ctx.obj["passman"].get_vault(guid, keys)
