#!/usr/bin/env python3
"""中英对照 HTML 自检：标签闭合、锚点、目录链接、图/表/对照段数量、图片存在性。
用法: check_html.py paper.html
"""
import os, re, sys
from html.parser import HTMLParser

path = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: check_html.py paper.html")
s = open(path, encoding="utf-8").read()
# 注释里的模板示例不计入统计与校验
s = re.sub(r"<!--.*?-->", "", s, flags=re.S)

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.err = []
    def handle_starttag(self, t, a):
        if t in ("img", "br", "meta", "link", "hr", "input"): return
        self.stack.append(t)
    def handle_endtag(self, t):
        if not self.stack or self.stack[-1] != t:
            self.err.append((t, self.getpos()))
        else:
            self.stack.pop()

p = P(); p.feed(s)
ids = re.findall(r'<h[23] id="([^"]+)"', s)
links = [h for h in re.findall(r'<a href="#([^"]+)"', s) if h != "toc"]
missing = [h for h in links if h not in ids]
imgs = re.findall(r'<img src="([^"]+)"', s)
base = os.path.dirname(os.path.abspath(path))
noimg = [i for i in imgs if not os.path.exists(os.path.join(base, i))]

print("标签错误:", p.err[:5], "未闭合:", p.stack[-5:])
print("锚点:", len(ids), "唯一:", len(set(ids)), "失效链接:", missing)
print("图:", s.count('<div class="figure">'), "表:", s.count("<table>"),
      "对照段:", s.count('class="pair"'), "算法:", s.count('class="algo"'))
print("缺失图片:", noimg)
ok = not p.err and not p.stack and not missing and not noimg
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
