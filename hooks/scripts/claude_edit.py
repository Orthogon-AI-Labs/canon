"""The text Claude Code's Edit tool writes, transcribed from Claude Code 2.1.312.

The edit guard judges the file the tool will actually write, so it can't use a plain
str.replace. The tool also matches an old_string that differs from the file only in curly
quotes or \\uXXXX escapes, restyles new_string to match what it found, and, when new_string
is empty, deletes the newline after old_string too. Function names in the comments are the
minified ones in the 2.1.312 bundle.
"""

from __future__ import annotations

import re

LEFT_SINGLE, RIGHT_SINGLE, LEFT_DOUBLE, RIGHT_DOUBLE = "‘", "’", "“", "”"
OPENING_CONTEXT = {" ", "\t", "\n", "\r", "(", "[", "{", "—", "–"}
ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")


def apply_edits(content: str | None, edits: list[tuple[str, str, bool]]) -> str | None:
    """The file's text after the edits (old_string, new_string, replace_all), applied in order,
    or None if the tool would refuse the call. content is None for a file that doesn't exist."""
    text = "" if content is None else content.replace("\r\n", "\n")
    original = text
    earlier_new: list[str] = []
    for old, new, replace_all in edits:
        if old == new:
            return None
        if old == "":
            # An empty old_string only creates a file (or fills an empty one).
            if content is not None and not all(c.isspace() or c == "﻿" for c in text):
                return None
            text = new
        else:
            actual = actual_old_string(text, old)
            if actual is None or (text.count(actual) > 1 and not replace_all):
                return None
            stripped = old.rstrip("\n")
            if any(stripped and stripped in earlier for earlier in earlier_new):
                return None  # "old_string is a substring of a new_string from a previous edit"
            before = text
            text = replace(text, actual, escaped_new_string(old, actual, styled_new_string(old, actual, new)), replace_all)
            if text == before:
                return None
        earlier_new.append(new)
    return None if text == original else text


def replace(content: str, old: str, new: str, replace_all: bool) -> str:  # B()
    if new == "" and not old.endswith("\n") and old + "\n" in content:
        old += "\n"
    return content.replace(old, new) if replace_all else content.replace(old, new, 1)


def actual_old_string(content: str, old: str) -> str | None:  # yDe()
    """The text in the file the tool will replace for this old_string, or None if it finds none."""
    if old in content:
        return old
    index = straight_quotes(content).find(straight_quotes(old))
    if index != -1:
        return content[index:index + len(old)]
    if ESCAPE_RE.search(old):
        decoded = from_units(unescape(to_units(old)))
        if decoded != old and decoded in content:
            return decoded
    if any(ord(c) >= 0x80 for c in old):
        units = to_units(content)
        if escaped_length(to_units(old)) > len(units) or "\\u" not in content:
            return None
        found = find_escaped(to_units(old), units)
        return None if found is None else from_units(found)
    return None


def straight_quotes(text: str) -> str:  # b()
    return (text.replace(LEFT_SINGLE, "'").replace(RIGHT_SINGLE, "'")
            .replace(LEFT_DOUBLE, '"').replace(RIGHT_DOUBLE, '"'))


def styled_new_string(old: str, actual: str, new: str) -> str:  # z_t()
    """new_string with straight quotes curled when old_string matched curly ones."""
    if old == actual:
        return new
    if LEFT_DOUBLE in actual or RIGHT_DOUBLE in actual:
        new = "".join(
            (LEFT_DOUBLE if opens(new, i) else RIGHT_DOUBLE) if c == '"' else c for i, c in enumerate(new)
        )
    if LEFT_SINGLE in actual or RIGHT_SINGLE in actual:
        chars = []
        for i, c in enumerate(new):
            if c != "'":
                chars.append(c)
            elif 0 < i < len(new) - 1 and new[i - 1].isalpha() and new[i + 1].isalpha():
                chars.append(RIGHT_SINGLE)  # an apostrophe inside a word
            else:
                chars.append(LEFT_SINGLE if opens(new, i) else RIGHT_SINGLE)
        new = "".join(chars)
    return new


def opens(text: str, index: int) -> bool:  # N()
    return index == 0 or text[index - 1] in OPENING_CONTEXT


# \uXXXX matching works on UTF-16 code units, as JavaScript strings do. These helpers take
# and return "unit strings": one Python character per UTF-16 code unit.

def to_units(text: str) -> str:
    data = text.encode("utf-16-le", "surrogatepass")
    return "".join(chr(data[i] | data[i + 1] << 8) for i in range(0, len(data), 2))


def from_units(units: str) -> str:
    return units.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass")


def unescape(units: str) -> str:  # _()
    return re.sub(r"(\\\\)|\\u([0-9a-fA-F]{4})",
                  lambda m: m.group(0) if m.group(1) is not None else chr(int(m.group(2), 16)), units)


def escaped_length(units: str) -> int:  # C()
    return len(units) + 5 * sum(1 for c in units if ord(c) >= 0x80)


def backslashes_before(units: str, index: int) -> int:  # R()
    count = 0
    while index - 1 - count >= 0 and units[index - 1 - count] == "\\":
        count += 1
    return count


def find_escaped(old: str, content: str) -> str | None:  # L()
    """The first place content spells old with \\uXXXX escapes for its non-ASCII units."""
    if backslashes_before(old, len(old)) % 2 == 1:
        return None
    starts = [0] if old[:1] == "\\" else []
    offset = 0
    pattern = []
    for c in old:
        if ord(c) >= 0x80:
            starts.append(offset)
            offset += 6
            pattern.append(r"\\u" + "".join(f"[{d}{d.upper()}]" if d >= "a" else d for d in f"{ord(c):04x}"))
        else:
            offset += 1
            pattern.append(re.escape(c))
    try:
        regex = re.compile("".join(pattern))
    except (re.error, RecursionError, OverflowError):
        return None
    position = 0
    while True:
        match = regex.search(content, position)
        if match is None:
            return None
        at = match.start()
        if all(backslashes_before(content, at + start) % 2 == 0 for start in starts):
            return match.group(0) if content.find(match.group(0)) == at else None
        position = at + 1


def escaped_new_string(old: str, actual: str, new: str) -> str:  # e9n()
    """new_string written the way old_string was found: escaped, or with escapes decoded."""
    if old == actual:
        return new
    old_u, actual_u, new_u = to_units(old), to_units(actual), to_units(new)
    if (any(ord(c) >= 0x80 for c in old_u) and escaped_length(old_u) == len(actual_u)
            and find_escaped(old_u, actual_u) is not None):
        digits_for: dict[int, str] = {}
        upper = lower = 0
        position = 0
        for c in old_u:
            if ord(c) >= 0x80:
                digits = actual_u[position + 2:position + 6]
                digits_for[ord(c)] = digits
                lower += sum(1 for d in digits if "a" <= d <= "f")
                upper += sum(1 for d in digits if "A" <= d <= "F")
                position += 6
            else:
                position += 1

        def escape(match: re.Match) -> str:
            code = ord(match.group(0))
            if code in digits_for:
                return "\\u" + digits_for[code]
            digits = f"{code:04x}"
            return "\\u" + (digits.upper() if upper > lower else digits)

        return from_units(re.sub("[\u0080-￿]", escape, new_u))
    if ESCAPE_RE.search(old_u) and unescape(old_u) == actual_u:
        return from_units(unescape(new_u))
    return new
