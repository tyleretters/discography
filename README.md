# Discography of Tyler Etters

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- EPs are defined as being less than or equal to 29 minutes 59 seconds.

## Publishing Instructions

- Update `discography.yml`
- `npm run convert` (convert yml to ts)
- `npm run build` (build dist ready js)
- `git add . && git commit -m "++" && git push origin main`
- qa on github
- `npm version patch`
- `npm publish --otp=<via_1password>`

## Usage Instructions

- `npm i @tyleretters/discography`
- `import discography from '@tyleretters/discography'`

## Development Instructions

- clone discography
- `cd discography`
- `chmod 700 src/convert.py`
- `npm run dev`
