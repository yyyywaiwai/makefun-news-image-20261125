#!/usr/bin/env python3
"""make.fun entry: news-image-20261125.

The repository ships a single newspaper front page, ``entry.png``,
summing up 25 November 2026's world news. This script is the entry
point: it copies that image into the output directory the grader
provides and checks the copy is complete and unchanged.

Only the standard library is used. Nothing is fetched, nothing is
random, and no clock is read, so repeated runs write identical bytes.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024


def png_dimensions(path):
    """Return (width, height) for a PNG, or raise ValueError."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33:
        raise ValueError("file too short to be a PNG")
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("missing PNG signature")
    if header[12:16] != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_image(path):
    """Check the front page meets the bounty limits; return its size."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError(f"image is {size} bytes, over the 1 MiB limit")
    width, height = png_dimensions(path)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"image is {width}x{height}, over 1024x1024")
    return width, height, size


def digest(path):
    """SHA-256 hex digest of a file, streamed in 1 MiB chunks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def run():
    """Copy the front page to the output directory and verify the copy."""
    try:
        width, height, size = check_image(SOURCE)
    except (OSError, ValueError) as exc:
        print(f"error: {SOURCE}: {exc}", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, destination)

    if os.path.getsize(destination) != size:
        print("error: copied file has a different size", file=sys.stderr)
        return 1
    if digest(SOURCE) != digest(destination):
        print("error: copied file has a different sha256", file=sys.stderr)
        return 1

    print(f"wrote {destination} ({width}x{height}, {size} bytes,"
          " sha256 verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
