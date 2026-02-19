#!/usr/bin/env python3

"""Scrape a Bandcamp album page and generate a discography.yml entry.

Usage:
    python3 src/scrape_bandcamp.py <bandcamp_url> [options]

Options:
    --my-artist <name>   Your artist name on this release (auto-detects your tracks)
    --project <name>     Your project name for this release
    --role <role>        Your role (default: Artist)
    --add                Prepend the generated entry to discography.yml

Example:
    python3 src/scrape_bandcamp.py https://synergybeat.bandcamp.com/album/synergy-beat-music-volume-1 \\
        --my-artist "The Future World Neural Net" \\
        --project "The Future World Neural Net" \\
        --role Artist \\
        --add
"""

import argparse
import html as html_mod
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from typing import Optional

import yaml

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
YML_PATH = os.path.join(DIR_PATH, "discography.yml")


def fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read().decode("utf-8")


def parse_bandcamp_data(html: str) -> dict:
    match = re.search(r'data-tralbum="([^"]+)"', html)
    if not match:
        raise ValueError(
            "Could not find album data in page. "
            "Is this a Bandcamp album URL (not a track or artist page)?"
        )
    decoded = html_mod.unescape(match.group(1))
    return json.loads(decoded)


def seconds_to_length(seconds: float) -> str:
    s = int(seconds)
    h, remainder = divmod(s, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def to_long_now(date_str: str) -> str:
    """Convert Bandcamp date string to Long Now format (e.g. '02018-10-31')."""
    # Bandcamp format: "31 Oct 2018 00:00:00 GMT"
    dt = datetime.strptime(date_str, "%d %b %Y %H:%M:%S GMT")
    return f"0{dt.year}-{dt.month:02d}-{dt.day:02d}"


def clean_title(title: str, artist: str) -> str:
    """Strip 'Artist - ' prefix from title if present (common on Bandcamp compilations)."""
    prefix = artist + " - "
    if title.startswith(prefix):
        return title[len(prefix):]
    return title


def prompt(message: str, default: Optional[str] = None) -> str:
    if default is not None:
        raw = input(f"{message} [{default}]: ").strip()
        return raw if raw else default
    return input(f"{message}: ").strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape a Bandcamp album and generate a discography.yml entry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", help="Bandcamp album URL")
    parser.add_argument("--my-artist", help="Your artist name (auto-detects your tracks)")
    parser.add_argument("--project", help="Your project name for this release")
    parser.add_argument("--role", help="Your role on this release (e.g. Artist, Producer, Remixer)")
    parser.add_argument("--add", action="store_true", help="Prepend the entry to discography.yml")
    args = parser.parse_args()

    print(f"Fetching {args.url} ...")
    try:
        html = fetch_page(args.url)
    except Exception as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = parse_bandcamp_data(html)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing page: {e}", file=sys.stderr)
        sys.exit(1)

    album_title = data["current"]["title"]
    label = data["artist"]
    raw_date = data["current"].get("release_date") or data["current"].get("publish_date")
    released = to_long_now(raw_date) if raw_date else "0????-??-??"
    bandcamp_credits = (data["current"].get("credits") or "").strip()
    bandcamp_about = (data["current"].get("about") or "").strip()

    tracks = sorted(data["trackinfo"], key=lambda t: t["track_num"])

    # Display the full track listing
    print(f"\n  Album   : {album_title}")
    print(f"  Label   : {label}")
    print(f"  Released: {released}")
    if bandcamp_about:
        print(f"  About   : {bandcamp_about[:120]}{'...' if len(bandcamp_about) > 120 else ''}")
    print(f"\n  Tracks:")
    for t in tracks:
        cleaned = clean_title(t["title"], t["artist"])
        dur = seconds_to_length(t["duration"])
        print(f"    {t['track_num']:2d}. [{t['artist']}] {cleaned} ({dur})")

    # Detect or prompt for user's tracks
    my_track_nums: list[int] = []
    if args.my_artist:
        my_track_nums = [t["track_num"] for t in tracks if t["artist"] == args.my_artist]
        if my_track_nums:
            print(f"\n  Auto-detected your tracks: {my_track_nums}")
        else:
            print(f"\n  Warning: no tracks found for artist '{args.my_artist}'")
            print(f"  Artists on this release: {sorted(set(t['artist'] for t in tracks))}")

    if not my_track_nums:
        raw = prompt(
            "\nEnter your track number(s) (comma-separated, or 'all' to include all)",
            "all",
        )
        if raw.lower() == "all":
            my_track_nums = [t["track_num"] for t in tracks]
        else:
            try:
                my_track_nums = [int(n.strip()) for n in raw.split(",")]
            except ValueError:
                print("Error: invalid track numbers", file=sys.stderr)
                sys.exit(1)

    # Prompt for release metadata
    print()
    project = args.project or prompt("Your project name")
    role = args.role or prompt("Your role", "Artist")

    default_notes = bandcamp_about if bandcamp_about else None
    notes_prompt = "Notes (leave blank for null)"
    raw_notes = prompt(notes_prompt, bandcamp_about or "")
    notes = raw_notes.strip() if raw_notes.strip() else None

    default_credits = bandcamp_credits or f"{project} is Tyler Etters."
    credits = prompt("Credits", default_credits)

    # Build the entry dict — key order matches discography.yml conventions
    entry: dict = {
        "title": album_title,
        "project": project,
        "released": released,
        "type": "Compilation",
        "format": "Digital",
        "role": role,
        "label": label,
        "mp3": False,
        "wav": False,
        "tracks": [],
        "streams": [{"platform": "Bandcamp", "url": args.url}],
        "notes": notes,
        "credits": credits,
    }

    for t in tracks:
        cleaned = clean_title(t["title"], t["artist"])
        entry["tracks"].append({
            "number": t["track_num"],
            "artist": t["artist"],
            "title": cleaned,
            "length": seconds_to_length(t["duration"]),
        })

    # Serialize to YAML
    # PyYAML doesn't support str | None type hints natively on older versions; cast to str for sort_keys
    yaml_str = yaml.dump(
        [entry],
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )

    print("\n--- Generated YAML ---\n")
    print(yaml_str)

    if args.add:
        try:
            with open(YML_PATH, "r") as f:
                existing = f.read()
            with open(YML_PATH, "w") as f:
                f.write(yaml_str + existing)
            print(f"Prepended to {YML_PATH}")
            print("Review the entry, then run: npm run build")
        except OSError as e:
            print(f"Error writing to {YML_PATH}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Run with --add to prepend directly to discography.yml")


if __name__ == "__main__":
    main()
