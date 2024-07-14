# Discography of Tyler Etters

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- EPs are defined as being less than or equal to 29 minutes 59 seconds.

## Updating & Publishing

- Update `./src/discography.yml`
- `npm run convert && npm run build` (convert yml to ts & build dist ready js)
- `git add . && git commit -m "++" && git push origin main`
- QA: [https://github.com/tyleretters/discography](https://github.com/tyleretters/discography)
- `npm version patch`
- `npm publish --otp=<via_1password>`

## Downstream Implementations

- `npm i @tyleretters/discography`
- `import discography from '@tyleretters/discography'`
