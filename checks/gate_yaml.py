#!/usr/bin/env python3
"""Minimal YAML reader for the gate's own config files.

Reads the small subset of YAML used by approvals.yaml and overrides.yaml:
- "# comments" and blank lines
- "key: value" and "key:" (nested mapping by indent)
- "- value" (scalar list items)
- "- key: value" (list items that are mappings, with deeper-indented
  continuation lines)
- quoted scalars ('...' or "..."), "[]" empty lists

It is deliberately NOT a full YAML parser. If a file uses anything
outside this subset, it raises ValueError with the line number instead
of guessing. That is the point: a config the gate cannot read exactly is
a config the gate must not trust. No third-party dependency: the gate
runs with the standard library only.
"""
import re


class YamlError(ValueError):
    pass


def _scalar(text, line_no):
    text = text.strip()
    if text in ("[]",):
        return []
    if text in ("{}",):
        return {}
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    if text.startswith(("[", "{")) or text.startswith(("*", "&", "!")):
        raise YamlError(f"line {line_no}: unsupported YAML here: {text!r}")
    return text


def _lines(text):
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        if "#" in raw:
            # A "#" starts a comment unless it is inside quotes.
            stripped = raw
            in_single = in_double = False
            cut = None
            for j, ch in enumerate(raw):
                if ch == "'" and not in_double:
                    in_single = not in_single
                elif ch == '"' and not in_single:
                    in_double = not in_double
                elif ch == "#" and not in_single and not in_double:
                    cut = j
                    break
            if cut is not None:
                stripped = raw[:cut]
        else:
            stripped = raw
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if "\t" in stripped[:indent]:
            raise YamlError(f"line {i}: tabs are not allowed for indent")
        out.append((indent, stripped.strip(), i))
    return out


def parse(text):
    """Parse the YAML subset into dicts, lists, and strings."""
    lines = _lines(text)
    if not lines:
        return {}
    value, pos = _parse_block(lines, 0, lines[0][0])
    if pos != len(lines):
        raise YamlError(f"line {lines[pos][2]}: unexpected content after the document")
    return value


def _parse_block(lines, pos, indent):
    if pos >= len(lines):
        return {}, pos
    first_indent, first_text, first_no = lines[pos]
    if first_indent < indent:
        return {}, pos
    if first_text.startswith("- ") or first_text == "-":
        return _parse_list(lines, pos, first_indent)
    return _parse_mapping(lines, pos, first_indent)


def _parse_list(lines, pos, indent):
    items = []
    while pos < len(lines):
        line_indent, text, line_no = lines[pos]
        if line_indent != indent or not (text.startswith("- ") or text == "-"):
            break
        rest = text[1:].strip()
        if not rest:
            # "-": a nested block follows at a deeper indent.
            value, pos = _parse_block(lines, pos + 1, indent + 1)
            items.append(value)
            continue
        if ":" in rest and not rest.startswith(('"', "'")):
            # "- key: value": a mapping whose first pair is on this line.
            key, _, value_text = rest.partition(":")
            item = {key.strip(): _scalar(value_text, line_no)}
            pos += 1
            # Deeper-indented lines belong to this mapping.
            while pos < len(lines):
                sub_indent, sub_text, sub_no = lines[pos]
                if sub_indent <= indent or sub_text.startswith("- "):
                    break
                if ":" not in sub_text:
                    raise YamlError(f"line {sub_no}: expected 'key: value', got {sub_text!r}")
                sub_key, _, sub_value = sub_text.partition(":")
                sub_key = sub_key.strip()
                sub_value = sub_value.strip()
                if not sub_value:
                    nested, pos = _parse_block(lines, pos + 1, sub_indent + 1)
                    item[sub_key] = nested
                else:
                    item[sub_key] = _scalar(sub_value, sub_no)
                    pos += 1
            items.append(item)
        else:
            items.append(_scalar(rest, line_no))
            pos += 1
    return items, pos


def _parse_mapping(lines, pos, indent):
    mapping = {}
    while pos < len(lines):
        line_indent, text, line_no = lines[pos]
        if line_indent != indent or text.startswith("- "):
            break
        if ":" not in text:
            raise YamlError(f"line {line_no}: expected 'key: value', got {text!r}")
        key, _, value_text = text.partition(":")
        key = key.strip()
        value_text = value_text.strip()
        if not value_text:
            nested, pos = _parse_block(lines, pos + 1, indent + 1)
            mapping[key] = nested
        else:
            mapping[key] = _scalar(value_text, line_no)
            pos += 1
    return mapping, pos


def load_file(path):
    """Read a YAML-subset file. Returns dicts, lists, and strings."""
    with open(path, encoding="utf-8") as handle:
        return parse(handle.read())
