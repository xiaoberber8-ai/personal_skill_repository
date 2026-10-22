---
name: scholar-bilingual-paper
description: 把一篇英文论文 PDF 全文整理成 Scholar 风格的中英对照 HTML（左英右中、图表随文、算法双语、可点击目录）。当用户要求“论文中英对照翻译/对照阅读/学术翻译排版”或点名本 skill 时使用。默认禁用，不参与日常对话上下文，仅显式点名时读取。
---

# scholar-bilingual-paper

目标：输入一篇英文论文 PDF，输出**单文件自包含 HTML**：左侧英文原文、右侧中文译文逐段对照，图、表、算法伪代码原位插入，顶部双列目录可跳转。骨架见 `assets/template.html`，样式见 `assets/paper.css` 与 `assets/toc.css`。

## 依赖

- `poppler-utils`（`pdftotext`、`pdftoppm`）
- Python 3 + Pillow（`python3 -c "import PIL"`）
- 不依赖 PyMuPDF：它在部分环境装不上，直接用 poppler + PIL。

## 全流程

### 1. 建工作区并抽取源材料

```bash
bash scripts/prepare_source.sh paper.pdf ./proj
```

产出：

- `proj/paper_raw.txt`：按阅读流抽取的正文，用于**逐段翻译**；
- `proj/paper_layout.txt`：`-layout` 版，保留列位置，用于**核对表格数字**；
- `proj/pages/page-01.png …`：150 dpi 页面图，用于**定位并裁剪插图**。

论文是双栏排版时，`raw` 里两栏会交错，属正常现象：按语义重组段落，不要照抄行序。

### 2. 建立结构清单

用 `Grep`/`Read(offset,limit)` 按需读取，**不要把整份 txt 读进上下文**。先列出一级/二级标题、图号、表号、算法号、定义与引理编号，形成交付清单，例如：摘要、1–10 节、图 1–14、表 1–4、算法 1–6、参考文献。

### 3. 裁剪插图

1. 打开对应 `pages/page-XX.png` 目测图片边界（PDF pt 坐标）；
2. 写 `spec.json`：`{"fig1": {"page": 2, "box": [x0, y0, x1, y1]}}`（单位 pt，左上/右下）；
3. 执行：

```bash
python3 scripts/crop_figures.py spec.json ./proj/figures
```

比例换算 `px = pt × 150 / 72` 已内置。裁完逐张目检：常见问题是上下截断、右边缘缺一列、把正文裁进图里；坐标宁可留 2–3 pt 余量。

### 4. 分块写作 HTML

以 `assets/template.html` 为骨架、`assets/paper.css` 为样式（内联进 `<style>`），每次只写 3–5 个小节，用占位符接续：

```html
<!--PART1--> … <!--PART2--> …
```

用 `Edit` 把上一个占位符替换成新内容，并在末尾留下下一个占位符。这样单次编辑可控，也不会一次性生成超长文件。

**对照单元**（最核心的标记）：

```html
<div class="pair">
  <div class="en">English paragraph, verbatim from the paper.</div>
  <div class="zh">对应中文译文，术语与符号沿用原文。</div>
</div>
```

规则：

- 英文栏**逐字保留原文**（含 `<i>`、上下标、引文编号），不要改写、不要省略；
- 中文栏按学术书面语翻译，符号用 `<i>`、`<sub>`、`<sup>` 还原，如 `<i>O</i>(<i>n</i>3<sup>λ/3</sup>)`；
- 段内小标题用 `<b>` 并同样双语，如 `<b>Datasets.</b>` / `<b>数据集。</b>`；
- 图：`<div class="figure"><img src="figures/figN.png"><div class="figcap">` 内放 `.en` 与 `.zh` 两条图题；
- 表：`<div class="table-wrap"><table><caption>` 英文表题 + `<span class="cn">` 中文表题，表头写 `Graph / 图` 这类双语列名；
- 算法：`<div class="algo">`，标题行双语，正文每行英文后跟 `<span class="cn-line">中文</span>`；
- 参考文献**保留英文原样**，不翻译；
- 页脚注明原文出处与“仅供课程学习”。

### 5. 表格数字核对（必做）

`raw` 抽取常把长数字截断或错位。每个表都要回到 `paper_layout.txt` 用 `Grep -n` 找表头附近原文逐行核对；列顺序也要以页面图为准（表头可能在抽取时被重排）。数字必须与原文一致。

### 6. 生成目录

```bash
python3 scripts/add_toc.py proj/paper_bilingual.html
```

脚本会：给所有 `h2/h3` 加锚点（`s1`、`s4-2` 形式）、在提示条后插入双列目录（中文标题 + 右侧英文小字）、补 `.toc` 样式、加右下角「↑ 目录」悬浮按钮、开启平滑滚动。重复执行安全（已有 `id="toc"` 时跳过）。

### 7. 质量检查

```bash
python3 scripts/check_html.py proj/paper_bilingual.html
```

检查项：标签闭合、锚点与目录链接、图/表/对照段数量、图片文件是否存在。随后本地起服务用浏览器目检一次（`python3 -m http.server`）：双栏是否对齐、表格是否溢出、图片是否破图或裁切、目录跳转是否正常。检查完关闭服务。

## 交付与目录约定

- 成品放项目目录，命名 `<论文简称>_中英对照.html`，图片放同级 `figures/`；
- 中间产物（`*_raw.txt`、`*_layout.txt`、`pages/`、`spec.json`）同目录保留，便于返工；
- 不修改原 PDF；不改写原文任何内容；
- 回复用户时给 `computer://` 绝对路径链接，并说明章节覆盖范围。

## 不要做的事

- 不要用 PyMuPDF；不要先机器翻译整篇再贴回（须逐段翻译，术语一致）；
- 不要把参考文献译成中文；
- 不要在正文里加入“与课件/参考资料对比”之类的话；
- 不要把整份抽取文本一次性读入上下文——按需 `Grep` + 分段读。
