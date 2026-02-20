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
npm run lint       # ESLint (TypeScript) + Ruff (Python)
npm publish        # Publish to npm (auto-builds via prepublishOnly)
```

```bash
source src/venv/bin/activate
pytest tests/      # Run Python test suite
```

Python scripts require the venv (see README Setup):

```zsh
cd src && source venv/bin/activate
```

## Project Structure

- `src/discography.yml` - Source of truth for all release data
- `src/convert.py` - Converts YAML to TypeScript, enriches data with slugs, URLs, and IDs
- `src/scrape_bandcamp.py` - Scrapes a Bandcamp album page and generates a discography.yml entry
- `src/types.ts` - TypeScript types and interfaces (Release, Track, Stream, union types for type/format/role)
- `src/index.ts` - Package entry point
- `tests/test_convert.py` - Test suite for the converter
- `dist/` - Built output (gitignored, included in npm tarball via `"files"` in package.json)

## Data Conventions

- **Dates**: Use "Long Now" format with leading `0` (e.g., `02025-11-18` not `2025-11-18`). Incomplete dates (`02006-??-??`) are acceptable for historical releases.
- **EPs**: Defined as releases ≤ 29:59 total length
- **IDs**: Generated via SHA256 hash of concatenated fields
- **Cover URLs**: Auto-generated from CDN base + project slug + release slug
- **Notes**: `"None."` is a valid note (displayed to user), while `null` means no notes exist
- **Streams**: Optional - not all releases have streaming platform URLs
- **Artistic content**: Some releases contain SSH keys or other technical artifacts as art; these are intentional

## Validation

The converter validates each release at build time:

- Required fields: `project`, `title`, `type`, `format`, `role`, `mp3`, `wav`, `notes`, `credits`
- `type` must be one of: Mix, LP, EP, Single, OST, Compilation, Triple LP, Demo
- `format` must be one of: Digital, CD-R, Vinyl, CD, CD Digital, Cassette Digital
- `role` must be one of: DJ, Artist, Producer, Musician, Band Member, Principal Musician, Operator
- `mp3` and `wav` must be booleans

## Release Schema

Each release in `discography.yml` has:

- `title`, `project`, `released`, `type`, `format`, `role`, `label`
- `mp3`, `wav` (booleans for availability)
- `tracks[]` with `number`, `title`, `length`; compilations also include per-track `artist`
- `streams[]` with `platform`, `url`
- `notes`, `credits`

The converter enriches these with `*_slug`, `*_url`, `runtime`, and `id` fields.

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
git add . && git commit -m "++"
npm version patch && npm publish
```

`npm publish` automatically runs `npm run build` via the `prepublishOnly` hook. No manual build step needed.
