"""
emit release data as toml.

the discography file is the hand-edited source of truth, so this emitter
optimizes for readability. it writes literal multi-line strings, keeps source
key order, and puts one array element per line.

third-party writers escape newlines or emit basic strings, which turns the
prose, ascii art, and key blocks into unreadable single-line values.
"""

from typing import Any

# keys that hold a list of sub-tables, in emit order
TABLE_KEYS = ("tracks", "streams")

# these values must stay strings. unquoted, toml reads "02026-07-04" as a date
# and "00:01:10" as a local time, which changes the type of the output json.
FORCE_QUOTE_KEYS = frozenset({"released", "length"})


def _check_emittable(value: str, key: str) -> None:
  """Reject values this emitter cannot represent safely."""
  if "'''" in value:
    raise ValueError(f"value for '{key}' contains ''' and cannot be a literal string")
  for char in value:
    if ord(char) < 32 and char not in "\n\t":
      raise ValueError(f"value for '{key}' contains a control character: {char!r}")


def format_string(value: str, key: str = "") -> str:
  """Format a string as a toml literal, multi-line when it holds newlines."""
  _check_emittable(value, key)
  if "\n" in value:
    # toml trims the newline directly after the opening delimiter, the same
    # way a yaml block scalar does. this keeps the trailing newline intact.
    return "'''\n" + value + "'''"
  if "'" in value:
    # a literal string cannot hold a single quote, so fall back to a basic
    # string. the corpus has no backslashes, so escaping quotes is enough.
    return '"' + value.replace('"', '\\"') + '"'
  return "'" + value + "'"


def format_value(value: Any, key: str = "") -> str:
  """Format a scalar or array as a toml value."""
  if isinstance(value, bool):
    return "true" if value else "false"
  if isinstance(value, int):
    return str(value)
  if isinstance(value, str):
    return format_string(value, key)
  if isinstance(value, list):
    if not value:
      return "[]"
    lines = [f"  {format_value(item, key)}," for item in value]
    return "[\n" + "\n".join(lines) + "\n]"
  raise TypeError(f"cannot emit value for '{key}': {value!r}")


def _emit_table(data: dict[str, Any], header: str, out: list[str]) -> None:
  """Emit one table, then any arrays of sub-tables it holds."""
  out.append(f"[[{header}]]")
  for key, value in data.items():
    if key in TABLE_KEYS:
      continue
    if isinstance(value, str) and key in FORCE_QUOTE_KEYS:
      _check_emittable(value, key)
      out.append(f"{key} = \"{value}\"")
    else:
      out.append(f"{key} = {format_value(value, key)}")

  for table_key in TABLE_KEYS:
    for row in data.get(table_key, []):
      out.append("")
      _emit_table(row, f"{header}.{table_key}", out)


def dump_releases(releases: list[dict[str, Any]]) -> str:
  """Serialize releases as a toml array of tables."""
  out: list[str] = []
  for release in releases:
    if out:
      out.append("")
    _emit_table(release, "release", out)
  return "\n".join(out) + "\n"
