# CLAUDE.md

This is an npm package containing a canonical discography of Tyler Etters's music releases.

## Tech Stack

- **Data source**: TOML (`src/discography.toml`)
- **Build**: Python script converts TOML to TypeScript, then Vite bundles for distribution
- **Output**: ES module published to npm as `@tyleretters/discography`

## Key Commands

Activate the venv first. `npm run convert` calls `python3`, so the build fails
without it:

```zsh
source venv/bin/activate
```

```bash
npm run build      # Full build: convert TOML → TS, compile, bundle
npm run convert    # Just run the Python converter
npm run lint       # ESLint (TypeScript) + Ruff (Python)
pytest tests/      # Run Python test suite
npm publish        # Publish to npm (auto-builds via prepublishOnly)
```

## Project Structure

- `src/discography.toml` - Source of truth for all release data
- `src/convert.py` - Converts TOML to TypeScript, enriches data with slugs, URLs, and IDs
- `src/toml_emit.py` - Writes release data as readable TOML, used by the scraper
- `src/scrape_bandcamp.py` - Scrapes a Bandcamp album page and generates a discography.toml entry
- `src/types.ts` - TypeScript types and interfaces (Release, Track, Stream, union types for type/format/role)
- `src/index.ts` - Package entry point
- `tests/test_convert.py` - Test suite for the converter
- `dist/` - Built output (gitignored, included in npm tarball via `"files"` in package.json)

## Data Conventions

- **Dates**: Use "Long Now" format with leading `0` (e.g., `02025-11-18` not `2025-11-18`). Incomplete dates (`02006-??-??`) are acceptable for historical releases.
- **EPs**: Defined as releases ≤ 29:59 total length
- **IDs**: Generated via SHA256 hash of concatenated fields
- **Cover URLs**: Auto-generated from CDN base + project slug + release slug
- **Notes**: `notes` is required and always a string. TOML has no null, so a release with nothing to say uses `"None."`, which is displayed to the user
- **Streams**: Optional - not all releases have streaming platform URLs
- **Artistic content**: Some releases contain SSH keys or other technical artifacts as art; these are intentional

## Editing discography.toml

The file is hand-edited, so follow the conventions the emitter writes:

- **Always quote `released` and `length`.** Unquoted, TOML reads `02026-07-04` as a date and `00:01:10` as a local time. Both feed the SHA256 IDs, so a type change silently churns every hash.
- **Use `'''` literal strings for multi-line prose, notes, and ASCII art.** Literal strings do not process escapes, so backslashes and quotes survive. A value that contains `'''` cannot be written this way.
- Each release is a `[[release]]` table. Tracks and streams are `[[release.tracks]]` and `[[release.streams]]`.
- TOML requires sub-tables after all scalar keys of their parent, so `tracks` and `streams` always come last in the file. `convert.py` restores the canonical key order (`KEY_ORDER`) when it loads, which keeps the generated output stable.
- Order is document order. Newest releases go at the top.

## Validation

The converter validates each release at build time:

- Required fields: `project`, `title`, `type`, `format`, `role`, `mp3`, `wav`, `notes`, `credits`
- `type` must be one of: Mix, LP, EP, Single, OST, Compilation, Triple LP, Demo, Anthology
- `format` must be one of: Digital, CD-R, Vinyl, CD, `CD, Digital`, `Cassette, Digital`
- `role` must be one of: DJ, Artist, Producer, Musician, Band Member, Principal Musician, Operator
- `mp3` and `wav` must be booleans

## Release Schema

Each release in `discography.toml` has:

- `title`, `project`, `released`, `type`, `format`, `role`, `label`
- `mp3`, `wav` (booleans for availability)
- `tracks[]` with `number`, `title`, `length`; compilations also include per-track `artist`
- `streams[]` with `platform`, `url`
- `notes`, `credits`

The converter enriches these with `*_slug`, `*_url`, `runtime`, and `id` fields.

## Adding a Compilation

Use `scrape_bandcamp.py` to pull data from a Bandcamp album page:

```zsh
source venv/bin/activate
python3 src/scrape_bandcamp.py <bandcamp_url> \
  --my-artist "Your Artist Name" \
  --project "Your Project Name" \
  --role Artist \
  --add
```

`--add` prepends the generated entry to `discography.toml`. Review the entry before building. Compilations use `type: Compilation`, `mp3: false`, `wav: false`, and include all tracks with per-track `artist` fields.

## Publishing

After updating `discography.toml`:

```zsh
source venv/bin/activate
git add . && git commit -m "++"
npm version patch && npm publish
```

`npm publish` automatically runs `npm run build` via the `prepublishOnly` hook. No manual build step needed.

Use `npm version major` when a change breaks consumers. Renaming or removing
`dist/discography.toml` is a breaking change, because that file ships in the
tarball.
