# Discography of Tyler Etters

[https://www.npmjs.com/package/@tyleretters/discography](https://www.npmjs.com/package/@tyleretters/discography)

[![npm version](https://img.shields.io/npm/v/@tyleretters/discography)](https://www.npmjs.com/package/@tyleretters/discography)

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- EPs are defined as being less than or equal to 29 minutes 59 seconds.

## Setup

- `cd discography`
- `npm i`
- `cd src`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

## Updating & Publishing

### One Shot

```zsh
cd src && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd ../ &&npm run build && git add . && git commit -m "++" && git push origin main && npm version patch && npm publish
```

### Sequential

- Update `./src/discography.yml`
- `npm run build` (convert yml to ts & build dist ready js)
- `git add . && git commit -m "++" && git push origin main`
- QA: [https://github.com/tyleretters/discography](https://github.com/tyleretters/discography)
- `npm version patch`
- `npm publish`

## Downstream Implementations

- `npm i @tyleretters/discography`
- `import discography from '@tyleretters/discography'`
