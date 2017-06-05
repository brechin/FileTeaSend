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

Simply run `filetea` command with file that you want to share.

If you want to reduce verbose output, edit `fileteasend/app.py` and change
the line 12 `logging.basicConfig(level=logging.DEBUG)` to
`logging.basicConfig(level=logging.INFO)` and rerun the setup install. Set
to `logging.basicConfig(level=logging.ERROR)` for no log output.
