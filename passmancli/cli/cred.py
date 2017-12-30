import click

@click.group("cred")
@click.pass_context
def entry_point(ctx):
  pass

@entry_point.command("show")
@click.option("--vault", "-v", required=True, help="Specify vault of the credential")
@click.option("--keys", "-k", required=False, help="Filter the result by list of comma separated keys")
@click.argument("guid")
@click.pass_context
def get_credential(ctx, vault, guid, keys=None):
  print ctx.obj["passman"].get_credential(vault, guid, keys)

@entry_point.command("create")
@click.option("--data", "-d", required=True,
              help="Use JSON to create a credential. See templates for more detail.")
@click.pass_context
def new_credential(ctx, data):
  print ctx.obj["passman"].new_credential(data)

@entry_point.command("update")
@click.argument("guid")
@click.option("--data", "-d", required=True,
              help="Use JSON to update a credential. See templates for more detail.")
@click.pass_context
def update_credential(ctx, guid, data):
  print ctx.obj["passman"].update_credential(guid, data)

@entry_point.command("delete")
@click.argument("guid")
@click.pass_context
def update_credential(ctx, guid):
  print ctx.obj["passman"].delete_credential(guid)
