# Skills 汇总


| Skills 名称 | 版本号 | 分类 | 标签 | 使用场景 / 人群 |
|---|---:|---|---|---|
| `data-office-pro` | 1.0.0 | 数据分析与办公提效 | `Excel`、`数据分析`、`ROI`、`投放复盘`、`数据可视化`、`报告`、`PPT`、`公式` | 适合运营、投放人员、数据分析师、管理者及日常办公用户；用于 Excel 数据处理、经营或广告投放复盘、ROI 测算、周报/月报、图表与汇报材料生成。 |
| `design-studio` | 1.0.0 | 视觉设计与交互原型 | `HTML`、`高保真原型`、`幻灯片`、`动画`、`信息图`、`UI Mockup`、`MP4/GIF`、`设计评审` | 适合产品经理、设计师、独立开发者和需要高质量视觉交付的团队；用于 HTML 高保真原型、演示文稿、产品动画、信息图、设计变体探索与专家评审。不适用于生产级 Web App 或需要后端的系统。 |
| `document-publishing` | 1.0.0 | 文档转换与数字出版 | `Markdown`、`HTML`、`DOCX`、`PDF`、`EPUB3`、`格式转换`、`出版排版`、`多端发布` | 适合研究人员和技术写作者；用于 PDF/DOCX/PPTX/XLSX/网页等转 Markdown，以及 Markdown 到 HTML、Word、PDF、EPUB 的出版级排版与多端分发。 |
| `markdown-to-pdf` | 1.0.0 | Markdown 文档排版 | `Markdown`、`PDF`、`白皮书`、`苹果风格`、`目录`、`页眉页脚`、`WeasyPrint` | 适合技术作者、开发者和报告撰写者；用于把带规范章节编号的 Markdown 转为带封面、目录、页眉页脚的专业 PDF，常见于技术文档、教程、白皮书和正式报告。 |
| `presentation-workflow` | 1.0.0 | 演示文稿制作 | `PPTX`、`Slides`、`Keynote`、`AI 插画`、`HTML2PPTX`、`设计风格`、`演示叙事` | 适合咨询顾问、产品经理、市场人员、培训讲师和汇报材料制作者；用于从内容结构、视觉系统、页面构建到 PPTX 组装和预览润色的端到端制作。 |
| `project-distiller` | 1.0.0 | 代码库理解与架构知识提炼 | `代码库分析`、`架构`、`调用链`、`模块边界`、`数据与状态`、`工程约束`、`Skill 生成` | 适合接手陌生项目的开发者、架构师、技术负责人和迁移/重构团队；用于从成熟代码库提炼真实入口、关键调用链、模块边界、扩展机制与设计原则，并沉淀为可复用的项目框架 Skill。 |
| `research-report` | 1.0.0 | 机构级研究与学术报告 | `行业报告`、`白皮书`、`年度调研`、`数据洞察`、`arXiv`、`图表系统`、`咨询 Deck`、`研究方法` | 适合研究员、学术作者；用于行业报告、白皮书、年度研究、数据洞察、学术论文和“一页一结论”的咨询型报告。单篇文章或纯演示 PPT 不属于其主要范围。 |
| `rigorous-data-analysis` | 1.0.0 | 严谨数据分析与质量控制 | `Excel`、`CSV`、`脏数据`、`数据清洗`、`指标口径`、`对账`、`可追溯`、`质量验证` | 适合数据分析师、财务、运营、审计、业务负责人和需要可信数字的决策团队；用于脏表体检、清洗、口径对齐、指标计算、差异排查、独立对账与可追溯报告，尤其适合回答“两个数为何对不上”和“这个数是否可靠”。 |

## 统一目录规范

每个 Skill 使用同一套 Codex 标准骨架：

```text
<skill-name>/
├── SKILL.md              # 必需：包含 name、description、metadata.version
├── agents/
│   └── openai.yaml       # 必需：界面名称、简介和默认调用提示
├── scripts/              # 可选：可重复执行的工具脚本
├── references/           # 可选：按需加载的说明和领域资料
└── assets/               # 可选：产出物会使用的模板、图片或其他素材
```

`scripts/`、`references/` 和 `assets/` 仅在 Skill 实际需要时存在，不创建空占位目录。历史兼容资源（如演示、示例或语料）可继续保留，但新增内容应优先归入上述标准目录。

## 分类概览

- **数据分析类**：`data-office-pro`、`rigorous-data-analysis`
- **设计与演示类**：`design-studio`、`presentation-workflow`
- **文档与出版类**：`document-publishing`、`markdown-to-pdf`
- **研究与报告类**：`research-report`
- **研发与架构类**：`project-distiller`

## 选用建议

- 日常办公、经营分析、投放复盘和快速汇报，优先使用 `data-office-pro`。
- 数据复杂、口径敏感、需要对账或结果必须经得起追问时，使用 `rigorous-data-analysis`。
- 要做高保真视觉、原型、动画或设计评审，使用 `design-studio`。
- 重点是从内容组织到成品 PPTX 的完整流程时，使用 `presentation-workflow`。
- 要建立 Markdown 为源、HTML/DOCX/PDF/EPUB 多端输出的出版流程，使用 `document-publishing`。
- 只需把规范 Markdown 快速转成固定苹果风格 PDF 时，使用 `markdown-to-pdf`。
- 要产出有研究方法、证据与机构级结构的长报告或论文，使用 `research-report`。
- 要理解成熟代码库并把架构知识沉淀成可复用 Skill，使用 `project-distiller`。
