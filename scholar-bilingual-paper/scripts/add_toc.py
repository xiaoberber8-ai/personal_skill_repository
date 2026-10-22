#!/usr/bin/env python3
"""给中英对照 HTML 加锚点 + 双列目录 + 返回目录按钮。

用法: add_toc.py paper.html [--split 6] [--title "目录 · CONTENTS"]
--split: 从第 N 节开始放到右列；默认按章节数对半切。
重复执行安全：已有 id="toc" 时直接退出。
"""
import argparse, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("html")
ap.add_argument("--split", type=int, default=None, help="右列从第 N 节开始")
ap.add_argument("--title", default="目录 · CONTENTS")
a = ap.parse_args()

path = a.html
s = open(path, encoding="utf-8").read()
if 'id="toc"' in s:
    print("已有目录，跳过")
    sys.exit(0)

def slug(num, en):
    return "s" + num.replace(".", "-") if num else en.split()[0].strip(".,:").lower()

spans = [(m.start(), m.end()) for m in re.finditer(r"<!--.*?-->", s, re.S)]
def in_comment(pos):
    return any(a <= pos < b for a, b in spans)

entries = []
def repl(m):
    if in_comment(m.start()):
        return m.group(0)
    lvl, raw = m.group(1), m.group(2)
    cn = re.search(r'<span class="cn">(.*?)</span>', raw)
    cn = cn.group(1) if cn else ""
    head = re.sub(r'<span class="cn">.*?</span>', "", raw).strip()
    num, en = "", head
    mm = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s+(.*)$", head)
    if mm:
        num, en = mm.group(1), mm.group(2)
    hid = slug(num, en)
    entries.append((lvl, num, en, cn, hid))
    return '<h%s id="%s">%s</h%s>' % (lvl, hid, raw, lvl)

s = re.sub(r"<h([23])>(.*?)</h\1>", repl, s, flags=re.S)
if not entries:
    sys.exit("未找到 h2/h3 标题")

if a.split is not None:
    idx = next((i for i, e in enumerate(entries) if e[1] == str(a.split)), len(entries) // 2)
else:
    idx = max(i for i, e in enumerate(entries) if e[0] == "2")
    idx = idx // 2 + 1

def items(es):
    out = []
    for lvl, num, en, cn, hid in es:
        cls = ' class="sub"' if lvl == "3" else ""
        label = '<span class="num">%s</span>' % num if num else '<span class="num">§</span>'
        out.append('    <a href="#%s"%s>%s%s<em>%s</em></a>' % (hid, cls, label, cn, en))
    return "\n".join(out)

toc = ('<div class="toc" id="toc">\n  <div class="toc-title">%s</div>\n'
       '  <div class="toc-grid">\n    <nav>\n%s\n    </nav>\n    <nav>\n%s\n    </nav>\n'
       '  </div>\n</div>\n') % (a.title, items(entries[:idx]), items(entries[idx:]))

anchor = s.find('<div class="notice">')
if anchor != -1:
    pos = s.index("</div>", anchor) + len("</div>")
else:
    m = re.search(r"</header>", s)
    pos = m.end() if m else s.index(">", s.index("<body")) + 1
s = s[:pos] + "\n\n" + toc + s[pos:]

# 补 TOC 样式
css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "toc.css")
if ".toc{" not in s and os.path.exists(css_path):
    css = open(css_path, encoding="utf-8").read()
    s = s.replace("</style>", css + "</style>", 1)

if 'class="to-top"' not in s:
    s = s.replace("</body>", '<a class="to-top" href="#toc">↑ 目录</a>\n</body>', 1)

open(path, "w", encoding="utf-8").write(s)
print("headings: %d, toc links: %d" % (len(entries), len(entries)))
