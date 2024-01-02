# Discography

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.

## Requirements

JSON script built with Python 3.11.5. See `src/convert.py` for required imports.

## Usage Instructions

- `npm i @tyleretters/discography`
- `import discography from '@tyleretters/discography'`

## Development Instructions

- clone discography
- `cd discography`
- `chmod 700 src/convert.py`
- `npm run dev`

## Convert YML

- `npm run convert`

## Publishing

- `npm run build`
- `npm publish`
