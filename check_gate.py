#!/usr/bin/env python3
"""Checker lokal yang meniru gate RULES untuk bounty ini.

Cek:
  1. main.py ada di root repo dan berjalan tanpa network (hanya PIL + stdlib,
     tidak ada import socket/requests/urllib/http).
  2. main.py menulis /output/entry.png (dihapus dulu sebelum run).
  3. File hasil adalah PNG/JPEG utuh, <= 1.048.576 byte, <= 1024x1024 px.
  4. Deterministik: dua run menghasilkan byte yang identik.
"""
import hashlib
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
OUT = "/output/entry.png"
MAX_BYTES = 1_048_576
MAX_DIM = 1024


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    from PIL import Image

    fails = []

    # 1. entrypoint + tanpa network
    main_py = os.path.join(REPO, "main.py")
    if not os.path.isfile(main_py):
        fails.append("main.py tidak ada di root repo")
    else:
        src = open(main_py, encoding="utf-8").read()
        for bad in ("socket", "requests", "urllib", "http.client",
                    "urlopen", "subprocess", "os.system"):
            if bad in src:
                fails.append(f"main.py mengandung {bad!r} (potensi network/shell)")
        if "PIL" not in src:
            fails.append("main.py tidak memakai PIL")

    # 2. run segar
    if os.path.exists(OUT):
        os.remove(OUT)
    r = subprocess.run([sys.executable, main_py], capture_output=True,
                       text=True, timeout=60, cwd=REPO)
    if r.returncode != 0:
        fails.append(f"main.py exit {r.returncode}: {r.stderr.strip()[-300:]}")
    if not os.path.exists(OUT):
        fails.append("/output/entry.png tidak ditulis")
        print("GAGAL:")
        for f in fails:
            print(" -", f)
        sys.exit(1)

    # 3. gate: format, ukuran byte, dimensi
    size = os.path.getsize(OUT)
    try:
        im = Image.open(OUT)
        im.verify()
        im = Image.open(OUT)
        fmt, (w, h) = im.format, im.size
    except Exception as e:  # noqa: BLE001
        fails.append(f"file bukan gambar utuh: {e}")
        fmt, w, h = "?", 0, 0
    if fmt not in ("PNG", "JPEG"):
        fails.append(f"format {fmt}, harus PNG/JPEG")
    if size > MAX_BYTES:
        fails.append(f"ukuran {size} byte > {MAX_BYTES}")
    if w > MAX_DIM or h > MAX_DIM:
        fails.append(f"dimensi {w}x{h} > {MAX_DIM}x{MAX_DIM}")

    # 4. determinisme
    h1 = sha(OUT)
    subprocess.run([sys.executable, main_py], capture_output=True,
                   timeout=60, cwd=REPO)
    h2 = sha(OUT)
    deterministic = h1 == h2

    print(f"format     : {fmt}")
    print(f"dimensi    : {w}x{h} (maks {MAX_DIM}x{MAX_DIM})")
    print(f"ukuran     : {size} byte (maks {MAX_BYTES})")
    print(f"sha256     : {h1}")
    print(f"deterministik: {'YA' if deterministic else 'TIDAK'}")
    if not deterministic:
        fails.append("dua run menghasilkan byte berbeda")
    if fails:
        print("GAGAL:")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("LOLOS: semua cek gate RULES terpenuhi.")


if __name__ == "__main__":
    main()
