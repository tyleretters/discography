# CLAUDE.md

This is an npm package containing a canonical discography of Tyler Etters's music releases.

## Tech Stack

- **Data source**: YAML (`src/discography.yml`)
- **Build**: Python script converts YAML to TypeScript, then Vite bundles for distribution
- **Output**: ES module published to npm as `@tyleretters/discography`

## Key Commands

```bash
npm run build      # Full build: convert YAML → TS, compile, bundle
npm run convert    # Just run the Python converter
```

Python scripts require the venv (see README Setup):

```zsh
cd src && source venv/bin/activate
```

## Project Structure

- `src/discography.yml` - Source of truth for all release data
- `src/convert.py` - Converts YAML to TypeScript, enriches data with slugs, URLs, and IDs
- `src/scrape_bandcamp.py` - Scrapes a Bandcamp album page and generates a discography.yml entry
- `src/types.ts` - TypeScript interfaces (Release, Track, Stream)
- `src/index.ts` - Package entry point
- `dist/` - Built output

## Data Conventions

- **Dates**: Use "Long Now" format with leading `0` (e.g., `02025-11-18` not `2025-11-18`). Incomplete dates (`02006-??-??`) are acceptable for historical releases.
- **EPs**: Defined as releases ≤ 29:59 total length
- **IDs**: Generated via MD5 hash of concatenated fields
- **Cover URLs**: Auto-generated from CDN base + project slug + release slug
- **Notes**: `"None."` is a valid note (displayed to user), while `null` means no notes exist
- **Streams**: Optional - not all releases have streaming platform URLs
- **Artistic content**: Some releases contain SSH keys or other technical artifacts as art; these are intentional

## Release Schema

Each release in `discography.yml` has:

- `title`, `project`, `released`, `type`, `format`, `role`, `label`
- `mp3`, `wav` (booleans for availability)
- `tracks[]` with `number`, `title`, `length`; compilations also include per-track `artist`
- `streams[]` with `platform`, `url`
- `notes`, `credits`

The converter enriches these with `*_slug`, `*_url`, and `id` fields.

## Adding a Compilation

Use `scrape_bandcamp.py` to pull data from a Bandcamp album page:

```zsh
cd src && source venv/bin/activate
python3 scrape_bandcamp.py <bandcamp_url> \
  --my-artist "Your Artist Name" \
  --project "Your Project Name" \
  --role Artist \
  --add
```

`--add` prepends the generated entry to `discography.yml`. Review the entry before building. Compilations use `type: Compilation`, `mp3: false`, `wav: false`, and include all tracks with per-track `artist` fields.

## Publishing

After updating `discography.yml`:

```zsh
npm run build
git add . && git commit -m "++"
npm version patch && npm publish
```
