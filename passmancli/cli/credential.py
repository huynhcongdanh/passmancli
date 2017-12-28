import click


@click.group("credential")
@click.pass_context
def entry_point(ctx):
  pass

@entry_point.command("get")
@click.option("--vault", "-v", required=True, help="Specify vault of the credential")
@click.argument("guid")
@click.pass_context
def get_credential(ctx, vault, guid):
  print ctx.obj["passman"].get_credential(vault, guid)


#@entry_point.command("new")
#@click.option("--data", "-d", required=True,
#              help="JSON used to create a credential"
#                   "(check https://github.com/nextcloud/passman/wiki/API)")
#def new_credential(ctx):
#  print ctx.obj["passman"].new_credential(json.loads(data))


#@entry_point.command("update")
#@click.option("--data", "-d", required=True,
#              help="JSON used to update a credential "
#                   "(check https://github.com/nextcloud/passman/wiki/API)")
#def update_credential(ctx):
#  print ctx.obj["passman"].update_credential(json.loads(data))
