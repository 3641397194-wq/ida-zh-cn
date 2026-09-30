#!/usr/bin/env python3
"""Sanity-check plugin/zh_cn.json (and an optional zh_cn_user.json).

    python tools/check_dict.py                # check the shipped dictionary
    python tools/check_dict.py path/to.json   # check another file

Exit status is non-zero if a hard problem is found, so CI can gate on it.

Hard errors
  * not valid UTF-8 JSON / not a flat {"english": "中文"} object
  * a value that is empty or has no CJK character (untranslated)
  * two keys that collapse to the same normalized key with *different* translations
Warnings
  * a key that still contains '&' or a trailing '...' (harmless: the plugin normalizes them, but the
    canonical form has neither)
  * a value that carries its own '(&X)' mnemonic or trailing '...' (the plugin strips and re-adds them)
"""
import json
import re
import sys
from pathlib import Path

CJK = re.compile(r"[㐀-鿿豈-﫿]")
# words that are legitimately left in English (brand names, protocol names, ...)
KEEP_ENGLISH_OK = {"Lumina", "IDA", "Python", "FLIRT", "Swift", "COM Helper"}


def norm(key: str) -> str:
    k = key.replace("&", "").replace("~", "").strip()
    for tail in ("...", "…"):
        if k.endswith(tail):
            k = k[: -len(tail)].rstrip()
    return k


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent / "plugin" / "zh_cn.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot read {path}: {exc}")
        return 1
    if not isinstance(data, dict):
        print("ERROR: top level must be a JSON object")
        return 1

    errors, warnings = [], []
    seen = {}
    total = 0
    for key, val in data.items():
        if key.startswith("_"):
            continue
        total += 1
        if not isinstance(val, str) or not val.strip():
            errors.append(f"empty or non-string value for {key!r}")
            continue
        nk = norm(key)
        if norm(val) == nk and nk not in KEEP_ENGLISH_OK:
            pass  # identical to source: allowed but useless
        elif not CJK.search(val) and nk not in KEEP_ENGLISH_OK and val.strip() != nk:
            errors.append(f"no Chinese characters in translation of {key!r}: {val!r}")
        if nk in seen and seen[nk][1] != val:
            errors.append(f"conflicting entries for {nk!r}: {seen[nk][0]!r}={seen[nk][1]!r} vs {key!r}={val!r}")
        seen.setdefault(nk, (key, val))
        if "&" in key or key.endswith("..."):
            warnings.append(f"key not in canonical form: {key!r}")
        if re.search(r"\(&.\)", val) or val.endswith("..."):
            warnings.append(f"value carries mnemonic/ellipsis (will be stripped): {key!r} -> {val!r}")

    print(f"{path.name}: {total} entries, {len(seen)} unique normalized keys")
    for w in warnings[:20]:
        print("  warn :", w)
    if len(warnings) > 20:
        print(f"  ... and {len(warnings) - 20} more warnings")
    for e in errors:
        print("  ERROR:", e)
    print("OK" if not errors else f"FAILED ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
