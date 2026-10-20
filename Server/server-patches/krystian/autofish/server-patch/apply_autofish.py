#!/usr/bin/env python3
"""apply_autofish.py <engine game/src dir>
Applies Auto-Fishing hybrid patch (MT2009_PLUS_AUTOFISH_V1) to server C++ engine.
"""
import json
import os
import sys

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src_dir = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    edits = json.load(open(os.path.join(here, "edits.json"), "r", encoding="utf-8"))

    files = {}
    for e in edits:
        path = os.path.join(src_dir, e["file"])
        if path not in files:
            files[path] = open(path, "rb").read().decode("latin-1")

    applied = 0
    for e in edits:
        path = os.path.join(src_dir, e["file"])
        text = files[path]
        if e["marker"] in text.replace("\r\n", "\n"):
            continue
        crlf = "\r\n" in text
        old = e["old"].replace("\n", "\r\n") if crlf else e["old"]
        new = e["new"].replace("\n", "\r\n") if crlf else e["new"]
        if text.count(old) != 1:
            sys.exit("autofish: marker %s expected code not found in %s" % (e["marker"], e["file"]))
        files[path] = text.replace(old, new, 1)
        applied += 1

    for path, text in files.items():
        before = open(path, "rb").read().decode("latin-1")
        if text != before:
            open(path, "wb").write(text.encode("latin-1"))
            print("autofish: %s updated" % os.path.basename(path))

    print("autofish: applied %d edit(s)" % applied)

if __name__ == "__main__":
    main()
