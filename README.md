# sshbox

![sshbox screenshot](image.png)

## Install:
`pipx install git+https://github.com/kwilt/sshbox.git`

## How To Use
- `sshbox` - connect to a host
- `sshbox add` - Add a new group or host to the configuration
- `sshbox edit` - Edit a group or host in the configuration
- `sshbox remove` - Remove a group or host from the configuration

## Config File

- Config file `sshbox.json` will be created in `~/.ssh/sshbox.json` when you first run the app
  - To override this behavior, set the `SSHBOX_CONFIG_FILE` environment variable to the path of your file.

  - A generic config file will be created when you first run the app

  - Example **Linux**: `export SSHBOX_CONFIG_FILE='/your/preferred/path/file_name.json'`
  - Example **Windows**: `SETX SSHBOX_CONFIG_FILE C:\your\preferred\path\file_name.json /M` (restart terminal after setting)

  - You can change the colors of text in the table by setting values in `table_colors`.
    - Valid color names are here: https://rich.readthedocs.io/en/stable/appendix/colors.html


## Template Config File For Reference
This will be generated when you run the app for the first time without an existing config file

```sshbox.json
{
  "app_settings": {
    "table_colors": {
      "selection_number": "cyan",
      "hostname": "yellow",
      "group": "green"
    }
  },
  "Development": {
    "web-host": {
      "hostname": "dev.example.com",
      "username": "devuser",
      "port": 22
    },
    "database": {
      "hostname": "db.dev.example.com",
      "username": "dbadmin",
      "port": 22
    }
  },
  "Production": {
    "web-host-1": {
      "hostname": "web1.example.com",
      "username": "produser",
      "port": 22
    },
    "web-host-2": {
      "hostname": "web2.example.com",
      "username": "produser",
      "port": 22
    },
    "database": {
      "hostname": "db.example.com",
      "username": "dbadmin",
      "port": 22
    }
  }
}
```
