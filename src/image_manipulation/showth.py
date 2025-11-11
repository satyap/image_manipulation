#!/usr/bin/env python3
"""
showth.py — Generate paginated HTML thumbnail galleries

This script scans the current directory for JPG images and creates
thumbnail versions (160×120) using ImageMagick's `convert` command.
It then generates simple HTML index pages (index.html, index2.html, …)
using a Jinja2 template (`tmpl.html`).

Features:
    • Automatically creates `th/` directory for thumbnails
    • Uses up to 8 threads for parallel thumbnail generation
    • Paginates output (12 images per page)
    • Adds next/previous navigation links
    • Optional "Up one level" link to parent directory (pass 1 as argument)

Dependencies:
    • Python 3.8+
    • Jinja2 (for templating)
    • ImageMagick (CLI `convert` command available in PATH)

Usage:
    python showth.py [linktoparent]

Example:
    python showth.py       # no parent link
    python showth.py 1     # include link to parent index

Typical folder layout:
    .
    ├── ar_l.png
    ├── ar_r.png
    ├── image1.jpg
    ├── image2.jpg
    ├── index.html
    ├── index2.html
    ├── th/
    │   ├── image1.th.jpg
    │   └── image2.th.jpg
    └── tmpl.html
"""

import os
import sys
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.resources import files

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from typing import List, Dict, Any

THUMB_DIR = "th"
THUMB_WIDTH = 160
THUMB_HEIGHT = 120
MAX_THREADS = 8
IMAGES_PER_PAGE = 12


def make_thumbnail(img_path: str, out_path: str, width: int, height: int) -> None:
    """Generate a thumbnail using ImageMagick's convert command."""
    subprocess.run(["convert", img_path, "-strip", "-resize", f"{width}x{height}", out_path], check=False)
    print(f"{img_path} -> {out_path}")


def get_image_info(img: str, width: int, height: int) -> Dict[str, Any]:
    """Collect metadata for an image."""
    st = os.stat(img)
    date_str = time.strftime("%b %d %Y", time.localtime(st.st_mtime))
    out_name = os.path.join(THUMB_DIR, os.path.splitext(os.path.basename(img))[0] + ".th.jpg")

    return {
        "name": img,
        "tname": out_name,
        "date": date_str,
        "ddate": st.st_mtime,
        "size": f"{st.st_size / 1024:.2f}kB",
        "width": width,
        "height": height,
    }


def render_page(page_data: List[Dict], i: int, total: int, tmpl: Template, linktoparent: bool = False) -> None:
    """Render paginated HTML pages using Jinja2."""
    prev_page = i - 1 if i > 1 else 0
    next_page = i + 1 if i < total else 0

    html = tmpl.render(
        data=page_data,
        prevlink=bool(prev_page),
        prev="" if prev_page == 1 else prev_page,
        next=next_page if next_page else 0,
        linktoparent=linktoparent,
        thispage=i,
    )

    out_file = f"index{i if i > 1 else ''}.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_file}")


def create_html(data: List[dict], linktoparent: bool) -> None:
    # Sort images (by name desc, then date desc)
    data.sort(key=lambda x: (x["name"].lower(), x["ddate"]), reverse=True)
    # Render template pages
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape(["html"]))
    tmpl = env.get_template("tmpl.html")

    pages = [data[i : i + IMAGES_PER_PAGE] for i in range(0, len(data), IMAGES_PER_PAGE)]
    total = len(pages)
    for i, page_data in enumerate(pages, start=1):
        render_page(page_data, i, total, tmpl, linktoparent)


def make_thumbnails(data: List[dict]) -> None:
    os.makedirs(THUMB_DIR, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(make_thumbnail, img["name"], img["tname"], THUMB_WIDTH, THUMB_HEIGHT)
            for img in data
            if not os.path.exists(img["tname"])
        ]
        for _ in as_completed(futures):
            pass


def main() -> None:
    start_time = time.time()
    linktoparent = bool(int(sys.argv[1])) if len(sys.argv) > 1 else False

    files = sorted(
        [f for f in os.listdir(".") if f.lower().endswith(".jpg") and not f.lower().endswith(".th.jpg")],
        key=lambda x: x.lower(),
    )

    if not files:
        print("No JPG files found.")
        return

    data = [get_image_info(f, THUMB_WIDTH, THUMB_HEIGHT) for f in files]

    make_thumbnails(data)
    create_html(data, linktoparent)

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
