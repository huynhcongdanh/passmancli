# NextCloud/OwnCloud PassmanCLI

**NextCloud/OwnCloud PassmanCLI.**

This CLI is used to access encrypted data from a [Passman](https://github.com/nextcloud/passman) instance.

Currently only support Python2!

**Credit**: This is a folk of [Douglas Camata]'s original work at https://github.com/douglascamata/passman_cli . The original project provided a good Python framework that I would like to reuse and improve based upon personal needs. 

## Installation
```bash
git clone https://github.com/huynhcongdanh/passmancli.git

cd passmancli

python2 setup.py install

passman --version
```

## Post-Installation: Config File (Required)

PassmanCLI requires a [ConfigParser] config file to save the base url of the instance as well as your username and password. You can send a path to the config file using the `--config` option of the command-line. 
By the default, it looks for a config named `.passmancli` at the current working dir or at `~/.passman/active`, in this exact order.

Here's an example of configuration: `~/.config/active`

```ConfigParser
base_url = "https://my.nextcloud/apps/passman/api/"
user = username
password = password
```

## Switch between multiple Passman accounts

PassmanCLI allow you to switch between accounts using `passman block [user]` command.

You will need to create the config file for each user account under `~/.passman/`

For example if you have your personal account `userA` and your team account `teamB`, and you have created 2 config files `~/.passman/userA` and `~/.passman/teamB` you can switch between them by:

`passman block userA`

or

`passman block teamB`

The command will make softlink `~/.passman/active` to the current active user config file.

## Uninstallation

```bash
pip2 uninstall passmancli
rm -rf /usr/local/bin/passman
```

## Development

1. Clone this repository
2. Install the development requirements: `pip install -r requirements.txt`
3. (Optional) Install the egg in `develop` mode: `python setup.py develop`

## Run from Docker
Note: Please make sure that you have the default config file at ~/.passman/default. If your config is 
different, just need to adjust the docker run command
```bash
docker build -t passmancli .

docker run --rm -v ~/.passman:/config passmancli:latest cred show a_credential -v a_vault

```


## Usage

To learn more about the usage please run `passman --help`.
```bash
#--------------------------------------------------#  
passman --help
Usage: passman [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config PATH          Path to Passman client config file
  -p, --vault_password TEXT  Specify vault password if different than login
                             password
  --version                  Show the version and exit.
  --help                     Show this message and exit.

Commands:
  block
  cred
  vault
  
#--------------------------------------------------#  
passman block --help
Usage: passman block [OPTIONS] USER

Options:
  --help  Show this message and exit.
  
#--------------------------------------------------#  
passman vault --help
Usage: passman vault [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  show
  list
 
#--------------------------------------------------#  
passman cred --help
Usage: passman cred [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  show
  create
  update
  delete
  
```