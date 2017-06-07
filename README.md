# FileTeaSend

Easy file transfer using FileTea service

## Installation

```bash
git clone https://github.com/brechin/FileTeaSend.git
virtualenv ./fileteavenv
source ./fileteavenv/bin/activate
cd FileTeaSend
python setup.py install
```

## Run

Simply run `filetea` command with `-h` or `--help` to read the help of
command. It's self explanatory.

## Options and arguments

You can specify FileTea server with `FILETEAURL` environment variable or
with `-l` or `--url` arguments.

The `-v` argument enable the verbose mode, you can repeat it to get more
verbose output.
