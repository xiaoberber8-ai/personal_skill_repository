# personal_skill_repository

个人全局技能仓库。每个子目录是一个可直接安装的 skill（含 `SKILL.md` 与配套脚本/模板）。

## 技能列表

### scholar-bilingual-paper

把英文论文 PDF 全文整理为 **Scholar 风格中英对照 HTML**：左栏英文原文、右栏中文译文，图/表/算法原位编排，顶部双列可点击目录。

- 处理链路：`pdftotext` 抽正文与表格 → `pdftoppm` 渲染页面 → PIL 按坐标裁图 → 分块双语写作 → 自动加锚点与目录 → 结构+浏览器双重校验
- 附带脚本：
  - `scripts/prepare_source.sh`：抽取 raw/layout 文本并渲染 150dpi 页面图
  - `scripts/crop_figures.py`：按 PDF pt 坐标裁剪插图
  - `scripts/add_toc.py`：为 h2/h3 加锚点、生成双列目录、加返回目录按钮
  - `scripts/check_html.py`：标签闭合、锚点、图片完整性自检
- 附带样式与骨架：`assets/paper.css`、`assets/toc.css`、`assets/template.html`

安装：把 `scholar-bilingual-paper/` 复制到 `~/.agents/skills/`。该技能默认禁用（登记在 `~/.trae-cn/skill-config.json` 的 `disabledSkills`），仅当对话中明确点名时才加载，不占用日常上下文。
