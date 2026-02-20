"""Tests for the YAML-to-TypeScript converter."""

import hashlib

import pytest

from convert import (
    cdn_path,
    enrich_release,
    format_runtime,
    make_html_paragraphs,
    make_id,
    make_slug,
    make_track_title,
    parse_length_seconds,
    validate_release,
)


def _make_release(**overrides):
    """Create a minimal valid release dict for testing."""
    base = {
        "title": "Test Album",
        "project": "Test Project",
        "released": "02024-01-01",
        "type": "LP",
        "format": "Digital",
        "role": "Artist",
        "label": "Test Label",
        "mp3": True,
        "wav": True,
        "tracks": [
            {"number": 1, "title": "Track One", "length": "03:30"},
            {"number": 2, "title": "Track Two", "length": "04:15"},
        ],
        "notes": "Some notes.",
        "credits": "Test credits.",
    }
    base.update(overrides)
    return base


# --- make_slug ---


class TestMakeSlug:
    def test_basic(self):
        assert make_slug("Hello World") == "hello-world"

    def test_ampersand(self):
        assert make_slug("Rock & Roll") == "rock-and-roll"

    def test_punctuation_removed(self):
        assert make_slug("It's a Test!") == "its-a-test"

    def test_multiple_spaces_collapsed(self):
        assert make_slug("Too  Many   Spaces") == "too-many-spaces"

    def test_hyphens_collapsed(self):
        assert make_slug("a - b") == "a-b"

    def test_special_slug_greek(self):
        assert make_slug("ΑΙΓΑΙΙΣ") == "aigaiis"

    def test_special_slug_fullwidth(self):
        assert make_slug("ＤＲＥＡＭＲＯＡＤ") == "dreamroad"

    def test_special_slug_diacritics(self):
        assert make_slug("nausicaä") == "nausicaa"


# --- make_id ---


class TestMakeId:
    def test_deterministic(self):
        assert make_id("hello") == make_id("hello")

    def test_different_inputs(self):
        assert make_id("hello") != make_id("world")

    def test_matches_sha256(self):
        expected = hashlib.sha256("test".encode("utf-8")).hexdigest()
        assert make_id("test") == expected


# --- parse_length_seconds ---


class TestParseLengthSeconds:
    def test_mm_ss(self):
        assert parse_length_seconds("03:30") == 210

    def test_hh_mm_ss(self):
        assert parse_length_seconds("01:30:00") == 5400

    def test_zero(self):
        assert parse_length_seconds("00:00") == 0

    def test_hh_mm_ss_mixed(self):
        assert parse_length_seconds("00:59:43") == 3583


# --- format_runtime ---


class TestFormatRuntime:
    def test_under_one_hour(self):
        assert format_runtime(210) == "03:30"

    def test_exactly_one_hour(self):
        assert format_runtime(3600) == "01:00:00"

    def test_over_one_hour(self):
        assert format_runtime(3661) == "01:01:01"

    def test_zero(self):
        assert format_runtime(0) == "00:00"


# --- make_html_paragraphs ---


class TestMakeHtmlParagraphs:
    def test_single_line(self):
        assert make_html_paragraphs("Hello.") == "<p>Hello.</p>"

    def test_multi_line(self):
        assert make_html_paragraphs("Line 1\nLine 2") == "<p>Line 1</p><p>Line 2</p>"

    def test_trailing_newline_stripped(self):
        assert make_html_paragraphs("Hello.\n") == "<p>Hello.</p>"


# --- make_track_title ---


class TestMakeTrackTitle:
    def test_normal_title(self):
        assert make_track_title("Normal Track") == "Normal Track"

    def test_special_title_hash(self):
        original = 'A White USB Drive With "HEXAGON" iStock Logo #1135496271'
        expected = 'A White USB Drive With "HEXAGON" iStock Logo &num;1135496271'
        assert make_track_title(original) == expected


# --- cdn_path ---


class TestCdnPath:
    def test_basic(self):
        result = cdn_path("my-project", "my-release")
        assert result == "https://d107e1o0dn11sc.cloudfront.net/my-project/my-release"


# --- validate_release ---


class TestValidateRelease:
    def test_valid_release(self):
        validate_release(_make_release())  # should not raise

    def test_missing_required_field(self):
        release = _make_release()
        del release["title"]
        with pytest.raises(ValueError, match="missing required field"):
            validate_release(release)

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="invalid type"):
            validate_release(_make_release(type="Mixe"))

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="invalid format"):
            validate_release(_make_release(format="Tape"))

    def test_invalid_role(self):
        with pytest.raises(ValueError, match="invalid role"):
            validate_release(_make_release(role="Singer"))

    def test_non_boolean_mp3(self):
        with pytest.raises(ValueError, match="non-boolean mp3"):
            validate_release(_make_release(mp3="yes"))

    def test_non_boolean_wav(self):
        with pytest.raises(ValueError, match="non-boolean wav"):
            validate_release(_make_release(wav="yes"))


# --- enrich_release ---


class TestEnrichRelease:
    def test_generates_slugs(self):
        result = enrich_release(_make_release())
        assert result["project_slug"] == "test-project"
        assert result["release_slug"] == "test-album"

    def test_explicit_slug_used(self):
        result = enrich_release(_make_release(slug="custom-slug"))
        assert result["release_slug"] == "custom-slug"

    def test_generates_cover_url(self):
        result = enrich_release(_make_release())
        assert result["cover_url"] == (
            "https://d107e1o0dn11sc.cloudfront.net/"
            "test-project/test-album/test-album.jpg"
        )

    def test_generates_download_urls_when_true(self):
        result = enrich_release(_make_release(mp3=True, wav=True))
        assert result["mp3_url"].endswith("test-album-mp3.zip")
        assert result["wav_url"].endswith("test-album-wav.zip")

    def test_no_download_urls_when_false(self):
        result = enrich_release(_make_release(mp3=False, wav=False))
        assert "mp3_url" not in result
        assert "wav_url" not in result

    def test_generates_id(self):
        result = enrich_release(_make_release())
        assert result["id"] == make_id("Test ProjectTest Album")

    def test_calculates_runtime(self):
        result = enrich_release(_make_release())
        # Track One: 3:30 (210s) + Track Two: 4:15 (255s) = 465s = 7:45
        assert result["runtime"] == "07:45"

    def test_formats_notes_as_html(self):
        result = enrich_release(_make_release(notes="Line one\nLine two"))
        assert result["notes"] == "<p>Line one</p><p>Line two</p>"

    def test_monospace_notes(self):
        result = enrich_release(_make_release(notes="ASCII art", monospaceNotes=True))
        assert result["notes"] == "<pre>ASCII art</pre>"

    def test_null_notes_preserved(self):
        result = enrich_release(_make_release(notes=None))
        assert result["notes"] is None

    def test_formats_credits_as_html(self):
        result = enrich_release(_make_release(credits="Credit line"))
        assert result["credits"] == "<p>Credit line</p>"

    def test_generates_track_ids(self):
        result = enrich_release(_make_release())
        for track in result["tracks"]:
            assert "id" in track
            assert len(track["id"]) == 64  # SHA256 hex length

    def test_generates_track_urls(self):
        result = enrich_release(_make_release(mp3=True, wav=True))
        track = result["tracks"][0]
        assert track["mp3_url"].endswith("01-track-one.mp3")
        assert track["wav_url"].endswith("01-track-one.wav")

    def test_no_track_urls_when_downloads_false(self):
        result = enrich_release(_make_release(mp3=False, wav=False))
        track = result["tracks"][0]
        assert "mp3_url" not in track
        assert "wav_url" not in track

    def test_generates_stream_ids(self):
        release = _make_release()
        release["streams"] = [{"platform": "Spotify", "url": "https://spotify.com/test"}]
        result = enrich_release(release)
        assert "id" in result["streams"][0]
        assert len(result["streams"][0]["id"]) == 64
