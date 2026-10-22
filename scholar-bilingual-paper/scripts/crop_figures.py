#!/usr/bin/env python3
"""按 PDF pt 坐标从 150dpi 页面图中裁剪插图。

spec.json 例:
{"fig1": {"page": 2, "box": [314, 168, 602, 302]}, "fig2": {"page": 3, "box": [...]} }
box = [x0, y0, x1, y1]，单位 pt，原点在页面左上角。

用法: crop_figures.py spec.json <figures_dir> [--pages <pages_dir>] [--dpi 150]
"""
import argparse, json, os
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("outdir")
ap.add_argument("--pages", default=None, help="页面图目录，默认 spec 同级的 pages/")
ap.add_argument("--dpi", type=float, default=150)
a = ap.parse_args()

pages = a.pages or os.path.join(os.path.dirname(os.path.abspath(a.spec)), "pages")
os.makedirs(a.outdir, exist_ok=True)
scale = a.dpi / 72.0
spec = json.load(open(a.spec, encoding="utf-8"))
for name, item in spec.items():
    page, box = int(item["page"]), item["box"]
    img_path = os.path.join(pages, "page-%02d.png" % page)
    im = Image.open(img_path)
    left, top, right, bottom = [int(round(v * scale)) for v in box]
    left, top = max(left, 0), max(top, 0)
    right, bottom = min(right, im.width), min(bottom, im.height)
    out = os.path.join(a.outdir, name + ".png")
    im.crop((left, top, right, bottom)).save(out)
    print("%-8s p%-2d %4dx%-4d -> %s" % (name, page, right - left, bottom - top, out))
