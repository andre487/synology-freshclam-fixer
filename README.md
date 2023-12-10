# Synology freshclam fixer

The script for periodically fixing ClamAV settings (Antivirus Essential package) to custom ones in Synology NAS.

This is necessary because of settings reset to default when Antivirus Essential package is updating.

## Why do you need this?

  * You have to use a private or alternative mirror in your private network
  * You are in Russia and you have to use alternative mirrors because ClamAV banned whole the country

## Usage

```
usage: synology-freshclam-fixer.py [-h] --config CONFIG [--result RESULT] [--dns-database-info DNS_DATABASE_INFO]
                                   [--database-mirror DATABASE_MIRROR] [--private-mirror PRIVATE_MIRROR] [--custom-value CUSTOM_VALUE]

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to freshclam.conf
  --result RESULT, -r RESULT
                        Path to result config, if empty it will be value of `--config`
  --dns-database-info DNS_DATABASE_INFO, -d DNS_DATABASE_INFO
                        Value for replace DNSDatabaseInfo option with another domain with TXT record about components
  --database-mirror DATABASE_MIRROR, -m DATABASE_MIRROR
                        Database mirror, can be multiple
  --private-mirror PRIVATE_MIRROR, -p PRIVATE_MIRROR
                        Private mirror, can be multiple
  --custom-value CUSTOM_VALUE, -s CUSTOM_VALUE
                        Custom config value, example: -s "Checks 12" -s "TestDatabases yes"
```

## Example

```sh
./synology-freshclam-fixer.py \
    --config data/freshclam.conf \
    --result data/changed-freshclam.conf \
    --dns-database-info 'cvd.clamav.example.net' \
    --database-mirror 'https://clamav-ru.ai-stv.ru' \
    --database-mirror 'https://unlix.ru/clamav' \
    --private-mirror 'https://packages.microsoft.com/clamav' \
    --custom-value 'Checks 12' \
    --custom-value 'ScriptedUpdates no'
```

Files difference after changes applied:

```diff
16c16
< DNSDatabaseInfo current.cvd.clamav.net
---
> DNSDatabaseInfo cvd.clamav.example.net
22c22
< ScriptedUpdates yes
---
> ScriptedUpdates no
26,27c26,29
< Checks 24
< DatabaseMirror database.clamav.net
---
> Checks 12
> DatabaseMirror https://clamav-ru.ai-stv.ru
> DatabaseMirror https://unlix.ru/clamav
> PrivateMirror https://packages.microsoft.com/clamav
```

## Setup in Synology NAS

Place the script `synology-freshclam-fixer.py` in some directory on the FS. 
For example, it can be `/usr/local/bin/synology-freshclam-fixer.py`.

Run `chmod +x /usr/local/bin/synology-freshclam-fixer.py`. Or you can run it like `python3 synology-freshclam-fixer.py`.

Setup periodical task using [Task Scheduler](https://kb.synology.com/en-us/DSM/help/DSM/AdminCenter/system_taskscheduler?version=6).
For example, you can run this script once a day with specified parameters.
Script should be runned under root user.

## Links

[Config manual](https://manpages.ubuntu.com/manpages/bionic/man5/freshclam.conf.5.html)

Trusted mirror: https://packages.microsoft.com/clamav/
