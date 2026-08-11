# Discography of Tyler Etters

[https://www.npmjs.com/package/@tyleretters/discography](https://www.npmjs.com/package/@tyleretters/discography)

[![npm version](https://img.shields.io/npm/v/@tyleretters/discography)](https://www.npmjs.com/package/@tyleretters/discography)

- This repo builds a canonical discography of the music of Tyler Etters.
- This discography is incomplete.
- The source of truth is `src/discography.toml`.
- Release dates are in a modified "Long Now" format, prefixed with `0`. This also solves for some date/object/string/parsing/conversion issues.
- EPs are defined as being less than or equal to 29 minutes 59 seconds.

## Setup

```zsh
cd discography
npm i
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```

## Adding a Compilation

```zsh
source venv/bin/activate
python3 src/scrape_bandcamp.py <bandcamp_url> \
  --my-artist "Your Artist Name" \
  --project "Your Project Name" \
  --role Artist \
  --add
```

Review the prepended entry in `src/discography.toml`, then build and publish as normal.

## Build

```zsh
source venv/bin/activate
npm run build
```

This runs the full pipeline: Python converter (TOML to TS), Vite bundler (ESM + UMD), TypeScript compiler (type declarations), and copies the source TOML to `dist/`.

Activate the venv first. `npm run convert` calls `python3`, so the build fails without it.

`dist/` is gitignored — built artifacts are not committed. The `"files"` field in `package.json` ensures `dist/` is always included in the npm tarball.

## Test

```zsh
source venv/bin/activate
pytest tests/
```

## Lint

```zsh
npm run lint
```

## Publishing

After updating `src/discography.toml`:

```zsh
git add . && git commit -m "++" && git push origin main
npm login
npm version patch
npm publish
```

`npm publish` automatically runs `npm run build` via the `prepublishOnly` hook, so there's no need to build manually before publishing.

## Downstream Implementations

```zsh
npm i @tyleretters/discography
```

```typescript
import discography from "@tyleretters/discography";
```

The default export and its types did not change in 4.0.0.

The tarball also carries the raw data file. In 4.0.0 it changed from
`dist/discography.yml` to `dist/discography.toml`. Update any code that reads
that path.
