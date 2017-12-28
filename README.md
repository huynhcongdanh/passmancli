# NextCloud/OwnCloud PassmanCLI

**NextCloud/OwnCloud PassmanCLI.**

This CLI is used to access encrypted data from a [Passman](https://github.com/nextcloud/passman) instance.

**Credit**: This is a folk of [Douglas Camata]'s original work at https://github.com/douglascamata/passman_cli . The original project provided a good Python framework that I would like to reuse and improve based upon personal needs. 

## Installation
```bash
git clone https://github.com/huynhcongdanh/passmancli.git

cd passmancli

python setup.py install

passman --version
```

## Post-Installation: Config File (Required)

PassmanCLI requires a [ConfigParser] config file to save the base url of the instance as well as your username and password. You can send a path to the config file using the `--config` option of the command-line. 
By the default, it looks for a config named `.passmancli` at the current working dir and at `~/.config/`, in this exact order.

Here's an example of configuration: `~/.config/.passmancli`

```ConfigParser
base_url = "https://my.nextcloud/apps/passman/api/"
user = username
password = password
```

## Uninstallation

```bash
pip uninstall passmancli
```

## Development

1. Clone this repository
2. Install the development requirements: `pip install -r requirements.txt`
3. (Optional) Install the egg in `develop` mode: `python setup.py develop`

## Usage

To learn more about the usage please run `passman --help`.
```bash
Usage: passman [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config PATH          Path to Passman client config file
  -p, --vault_password TEXT  Specify vault password if different than login
                             password
  --version                  Show the version and exit.
  --help                     Show this message and exit.

Commands:
  credential
  vault
```