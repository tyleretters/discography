# Discography

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- EPs are defined as being less than or equal to 29 minutes 59 seconds.

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

## Publishing

Whenever you update the `discography.yml` file, be sure to convert it to `discography.ts` with:

- `npm run convert`
- manually bump version number package.json only
- `npm update`
- `npm run build`
- `npm publish --otp=<via_1password>`
