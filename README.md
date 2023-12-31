# Discography

- This repo builds a canonical discography of the music of Tyler Etters in JSON.
- Edit the `src/data.yml` file then run `convert.py` to generate JSON.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- This discography is incomplete.

## Requirements

Built with Python 3.11.5. Imports:

- yaml
- json
- re
- hashlib
- datetime

## Instructions

- clone discography
- `cd discography/src`
- `chmod 700 convert.py`
- `./convert.py`
- `cat ../dist/data.json`
