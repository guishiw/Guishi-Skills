---
name: darwin-skill
description: "Darwin Skill 2.1 (达尔文.skill 2.1): validation-gated skill optimizer with a 9-dimension rubric, paired independent judges, test prompts, Git-backed rollback, and human checkpoints. Evaluates and improves SKILL.md files while keeping only independently validated changes. Use when user mentions \"优化skill\", \"skill评分\", \"自动优化\", \"auto optimize\", \"skill质量检查\", \"达尔文\", \"darwin\", \"帮我改改skill\", \"skill怎么样\", \"提升skill质量\", \"skill review\", \"skill打分\"."
---

# Darwin Skill 2.1

> **v2.1 · 2026-06-10** — keep/revert 棘轮从「绝对分数 delta」改为「**paired 同-judge 比较 + 奇数 N 多数决**」（绝对分数 ±8 judge 噪音淹没保守编辑的真实增益、是 false-revert 源；within-judge 比较消除换尺污染）。绝对分数降级为 triage-only。
> **v2.0 · 2026-05-28** — 吸收 Microsoft Research SkillLens（arXiv 2605.23899）的 9 维评分药方 + SkillOpt（arXiv 2605.23904）的 validation-gated 验证机制 + human in the loop 三层守关。
>
> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个skill优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后**实际跑出来的效果是否更好**。

---

## 评估 Rubric（9维度，总分100）

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证发现——LLM-as-judge 评估 skill 质量准确率仅 46.4%（接近随机），加入 meta-skill 三维度后提升到 73.8%。本 rubric 强化 dim3 / dim5 评分标准，新增 dim9「反例与黑名单」，权重平衡到 100。**目的：让评分对真实质量更敏感，减少 LLM judge 的乐观偏差。**

### 结构维度（59分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **Frontmatter质量** | 7 | name规范、description包含做什么+何时用+触发词、≤1024字符、**禁结尾加"灵活应用/根据情况判断"等空话尾巴** |
| 2 | **工作流清晰度** | 12 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **失败模式编码** | 12 | **必须显式编码失败模式**（写出"如果 X 失败 → Y"的明确分支）；有fallback路径、错误恢复；**只写正向流程而不写失败分支扣 ≥3 分**（SkillLens meta-skill 维度） |
| 4 | **检查点设计** | 6 | 关键决策前有用户确认、防止自主失控；**检查点必须显性标记（🔴/STOP/CHECKPOINT），仅靠"如果...建议..."措辞不算** |
| 5 | **可执行具体性** | 18 | 不模糊、有具体参数/格式/示例、可直接执行；**禁止"建议/可以考虑/根据情况/灵活把握/视情况而定"等软化措辞**——出现 ≥3 处扣 ≥3 分（SkillLens actionable specificity 维度） |
| 6 | **资源整合度** | 4 | references/scripts/assets引用正确、路径可达 |

### 效果维度（35分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 12 | 结构层次清晰、不冗余不遗漏、与原作者生态一致；**冗余/AI腔废话段落（说白了/换句话说/首先其次综上等原作者禁用词）出现一处扣 1 分** |
| 8 | **实测表现** | 23 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

### Meta-skill 维度（6分）— 反例与黑名单

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 9 | **反例与黑名单** | 6 | **skill 必须有"不要做什么"的反例清单**；只写"应该做 X"没有"不要做 Y"扣 ≥3 分；红灯/危险动作/反模式应单独章节列出（SkillLens risk-action blacklist 维度） |

### 评分规则
- 维度1-7、9：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度8（实测表现）：跑2-3个测试prompt，按输出质量打1-10分
- **总分 = Σ(维度分 × 权重) / 10**，满分100
- ⚠️ **绝对总分只用于 triage（粗排「哪支最弱、先改谁」），绝不用于 keep/revert**。实测：同一份**未改**文字换个 judge 评，总分可摆 **±8**（一支只加了 3 个 🔴 字元的 skill、单评却 −8.5，全是 judge 换尺、非真实退步）。keep/revert 一律走 **Phase 2 的 paired 比较**。
  - **为什么**：LLM judge 给的是**抽样、不是测量**——分数住在「文字 × 该 judge 当下选的标准」里，不是文字属性。绝对总分 = 用**两台未校准磅秤**量节食前后，差值大半是磅秤差；paired = **同一台磅秤**量前后，误差相减抵销。pairwise preference >> absolute scoring 是 LLM judge 的已知结论（RLHF 用 pairwise 不用绝对分同因）。

### Rubric 的实证基础

rubric 设计依据来自 **SkillLens 论文（arXiv 2605.23899）** + **本机 controlled study**：

- SkillLens 发现 LLM-as-judge 准确率仅 46.4%（接近随机），加入 meta-skill 三维度后升到 73.8%
- 本机对 research-workflow 做 4 类 degradation → 5 个独立 judge 盲测一致 V1>V2，Δ 均值 +46.5（5/5 high confidence）

**结论**：rubric 能识别 gross degradation，但 fine-grained quality difference 仍不可信，**重要决策必须人审**。

→ 详细论文证据 + 5 judges 完整数据 + HL 实战案例数字见 [references/skilllens-evidence.md](references/skilllens-evidence.md)

### 关于「实测表现」维度

这是与纯结构评分最大的区别。评分方式：

1. 为每个skill设计2-3个**典型用户prompt**（不是边缘case，是最常见的使用场景）
2. 用子agent执行：一个带skill跑，一个不带skill跑（baseline）
3. 对比输出质量，从以下角度打分：
   - 输出是否完成了用户意图？
   - 相比不带skill的baseline，质量提升明显吗？
   - 有没有skill引入的负面影响（过度冗余、跑偏、格式奇怪）？

若子 agent 不可用（超时/资源限制），退化为「干跑验证」：读完 skill 后模拟一个典型 prompt 的执行思路，判断流程是否合理；必须在 results.tsv 标注 `dry_run`。**dry_run 比例 > 30% → 评估失效警告**（来自本机 controlled study：dim8 实测维度权重 23%，无 full_test 验证时分数不可信）。

---

## Runtime 适配性审查（gate 项，独立于 9 维度评分）

skill 应当能在 Claude Code / Codex / Cursor / OpenClaw / Hermes / Gemini CLI / OpenCode 等 50+ skills-compatible runtime 通用——否则其他 agent 解析时会被「在 Claude Code 里」「Claude Code skill」等措辞误判为「不是给我用的」直接拒装（实例：nuwa-skill 因此被 Marvis agent 拒绝）。

### Phase 1 基线评估时强制跑一次红灯扫描

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

输出非空 = 红灯命中，**但须先读命中行上下文排除假阳性**（grep 命令本身/反例引用/讲解该规则的元陈述=假阳性，记 `runtime_scan=false_positive` 不改；判别表见 references/runtime-neutrality.md）→ 确认是真红灯（指令性用法）才强制把 Phase 2 第一轮定为 P0「runtime drift 修复」（写入 results.tsv 的 note 列 `runtime_warn=N`）。

### 例外（允许的「Claude Code 痕迹」）

frontmatter 触发词、原作者生态内部 skill 名引用、明确标注 runtime-specific 章节、commit message——这些正当出现，不算红灯。

→ 红灯/绿灯完整对照表 + 例外清单详细规则 + Phase 1/2/3 各阶段审查时机见 [references/runtime-neutrality.md](references/runtime-neutrality.md)

---

## 自主优化循环

### Phase 0: 初始化

```
1. 定位路径：
   - skill_root = 本 SKILL.md 所在目录（禁止假定安装在 `.claude/skills/`）
   - workspace_root = 用 `git -C <target_skill_dir> rev-parse --show-toplevel` 获取；失败则进入非 Git 降级模式
2. 确认优化范围：
   - 全部 skills → 从用户指定的 skills 根目录递归扫描 `SKILL.md`
   - 指定skills → 用户指定列表
3. Git 模式：记录当前分支和工作树状态，创建 `auto-optimize/YYYYMMDD-HHMM`
4. 非 Git 模式：不自动 `git init`；修改前将目标文件备份为 `SKILL.md.bak.YYYYMMDD-HHMMSS-r{round}`，并明确告知用户无 commit 级棘轮保障
5. 在 `skill_root/results.tsv` 初始化或读取历史记录
```

### Phase 0.5: 测试Prompt设计

在评估之前，为每个skill设计测试prompt。这步很关键——没有测试prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计2-3个测试prompt，覆盖：
     - 最典型的使用场景（happy path）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试prompt给用户，**确认后再进入评估**。测试prompt的质量决定了优化方向是否正确。

### Phase 1: 基线评估（Baseline）— triage 用途

> **本阶段绝对分数是 triage 排名（决定先改谁），不是 keep/revert 基准**。judge 对 gross 差异会一致（「哪支最弱」可信），对 fine-grained delta 不可信（±8 噪音）。keep/revert 在 Phase 2 用 paired 比较。

```
for each skill in 优化范围:

  # 结构评分（主agent可以做）
  1. 读取 SKILL.md 全文
  2. 按维度1-7逐项打分（附简短理由）

  # 效果评分（用子agent做，独立于主agent）
  3. 对每个测试prompt，spawn子agent：
     - with_skill: 带着SKILL.md执行测试prompt
     - baseline: 不带skill执行同一prompt
  4. 对比两组输出，打维度8的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**如果子agent不可用**（超时、环境限制），维度8用干跑验证打分，标注 `dry_run`。不要因为跑不了测试就跳过这个维度——哪怕是模拟推演也比完全不看效果好。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ proofreading      │ 78    │ 边界条件      │ 测试prompt2  │
│ presentation-workflow            │ 72    │ 指令具体性    │ baseline持平  │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ 平均                     │ 75    │              │              │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**🔴 CHECKPOINT · 🛑 STOP：暂停等用户确认，再进入优化循环。**

### Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    # Step 1: 诊断
    找出加权短板最大的维度：weighted_gap = weight × (10 - score) / 10，结构或效果都算
    # /10 与「总分 = Σ(维度分 × 权重) / 10」同标度：weighted_gap 就是该维度还能贡献的总分数
    # 为什么不用「原始分最低」：低权重维度会制造进步幻觉——issue #18 实战中
    # dim9（权重6，gap 5.3）原始分最低被优先修，而 dim8（权重23）加权短板最大（11.5）却 4 轮未动
    # 加权短板相近（差距 ≤ 1.0，同上述标度）时，回退为原始分升序
    # HL-3 警告：dim2/dim3/dim4 是相关簇，修一个时另两个常跟着涨
    # → 不要因为 dim3 短板最大就单独修，要看整簇短板再决定是否同步改

    # Step 2: 提出改进方案
    针对该维度，生成1个具体改进方案：
      - 改什么（具体段落/行）
      - 为什么改（对应rubric哪条）
      - 预期提升多少分

    # Step 3A: Git 模式（先固化改前版本，禁止提交后再把 HEAD 误当改前版）
    先校验目标 `SKILL.md` 的 staged/unstaged diff 均为空；若非空，停止并请用户先提交或备份
    base_commit = git rev-parse HEAD
    编辑 SKILL.md
    git add -- <workspace_root相对的skill-path>/SKILL.md
    提交前用 `git diff --cached --name-only` 校验暂存区只有本轮目标文件；若还有其他文件则停止并请用户处理，禁止混入提交
    git commit（message: "optimize {skill}: {改进摘要}"）
    candidate_commit = git rev-parse HEAD

    # Step 3B: 非 Git 模式
    每轮修改前复制为 `SKILL.md.bak.YYYYMMDD-HHMMSS-r{round}`，记录 base_hash
    编辑 SKILL.md 后记录 candidate_hash
    若两个 hash 相同，记 `status=error`并停止本轮

    # Step 4: Paired 重新评估（取代绝对重打分——绝对分数 judge 噪音 ±8、淹没保守编辑的 +3~8 真实增益）
    spawn N=3 独立 judge，每个【同一次 call 内】读两版：
      - Git 模式改前版：`git show ${base_commit}:<workspace_root相对的skill-path>/SKILL.md`
      - Git 模式改后版：`git show ${candidate_commit}:<workspace_root相对的skill-path>/SKILL.md`
      - 非 Git 模式：读本轮唯一 `.bak...-r{round}` 和当前 `SKILL.md`
    启动 judge 前：Git 模式校验 `base_commit != candidate_commit`；非 Git 模式校验 `base_hash != candidate_hash`；两种模式都要确认两份内容的 hash 不同。
    若相同，记 `status=error`并停止本轮，不得把同版比较记为 keep。
    照 9 维 rubric 当【比较准则】（不是各打绝对分），回 {better | worse | tie} + margin{clear|slight} + 一句理由。
    关键：同一 judge 在一次 call 内比两版 → 它那把不准的尺对两版【等量作用、在比较时抵销】(within-judge cancellation)，
    这正是 paired 优于绝对的机制。N 默认 3；首轮无绝对多数，或唯一多数方的所有票都是 `margin=slight`时，追加 2 个新 judge 升到 5。
    若 runtime 不支持独立 agent/隔离评审，禁止同 context 自评；展示两版 diff 并暂停，请用户完成 paired review。

    # Step 5: 共识决策（多数决，取代「新总分 > 旧总分」）
    cur = 投 better 的 judge 数；wor = 投 worse 的；
    if cur > N/2:
      status = "keep"
      # HL-4：仅统计 kept 轮次；连续 2 轮均是 better 绝对多数，且所有 better 票都为 margin=slight → break
    else if wor > N/2:
      status = "revert"
      Git 模式：先校验 `HEAD == candidate_commit`，再 `git revert ${candidate_commit}`；不相等则停止并人工处理
      非 Git 模式：用本轮的唯一 baseline 备份恢复目标 `SKILL.md`，恢复后校验 base_hash
      记录到 results.tsv（note 记 vote 比数 + 一句 worse 理由）
      break
    else:           # better 与 worse 同票，tie 不得被静默折算成 keep
      status = "review"
      展示 diff + 全部 judge 理由，等用户选择 keep / revert
    # 单评绝对分数出现「负 delta」≠ revert 信号；必须经 paired 多数判 worse 才 revert（否则在丢真实增益）

    # Step 6: 日志
    results.tsv 追加行

  # === 🔴 CHECKPOINT · 每个 skill 优化完后强制人审 ===
  展示该skill的改动摘要：
    - git diff（改前 vs 改后）
    - paired 票数、verdict 和 judge 理由（可选绝对分必须标明「非决策依据」）
    - 测试prompt输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个skill。
  如果用户说"不好"，回滚到该skill的优化前版本。
```

### Phase 2.5: 探索性重写（按需触发）

当 hill-climbing 连续2个skill都在 round 1 就 break（涨不动）时，提议一次「探索性重写」：

```
1. 选一个瓶颈skill
2. 将目标 `SKILL.md` 导出为唯一 baseline 快照并记录 hash；禁止全局 `git stash`
3. 从头重写 SKILL.md（不是微调，是重新组织结构和表达方式）
4. 重新评估
5. 复用 Phase 2 的 N=3/5 paired Judge 和绝对多数决：better 则采用重写版，worse 则恢复，无绝对多数则人审
```

这解决了 hill-climbing 的局部最优问题——有时候需要「先拆后建」才能突破瓶颈。
**🔴 CHECKPOINT · 🛑 STOP：必须征得用户同意后才执行。**

### Phase 3: 汇总报告

```
## 优化报告

### 总览
- 优化skills数：N
- 总实验次数：M
- 保留改进：X（Y%）
- 回滚次数：Z
- 实测验证：A次完整测试 / B次干跑

### Paired 验证（绝对分如展示，仅作 triage 参考）
┌──────────────────────────┬────────┬────────┬────────┐
│ Skill                    │ Before │ After  │ Δ      │
├──────────────────────────┼────────┼────────┼────────┤
│ proofreading      │ 78     │ 87     │ +9     │
│ presentation-workflow            │ 72     │ 83     │ +11    │
├──────────────────────────┼────────┼────────┼────────┤
│ 平均                     │ 75     │ 85     │ +10    │
└──────────────────────────┴────────┴────────┴────────┘

### 主要改进
1. [skill-A] 补充了边界条件处理，测试输出质量提升明显
2. [skill-B] 重组了workflow结构，baseline对比优势增大
```

---

## results.tsv 格式

```tsv
timestamp	commit	skill	before	after	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	proofreading	-	78.0	baseline	-	初始 triage 评估	full_test
2026-06-10T06:30	c4d5e6f	proofreading	a1b2c3d	3-0-0	keep	失败模式	better-worse-tie；补充 fallback	paired
```

`eval_mode` 列：`paired`（同 judge 比改前/改后，**keep/revert 权威依据**）｜`full_test`（子agent 跑 prompt）｜`dry_run`（模拟推演、仅供参考）。
paired 行：`before` 记 base commit/hash，`after` 按 `better-worse-tie` 记票数，`status` 记 keep/revert/review，`note` 记一句裁断理由。绝对分可写入 note 供 triage 参考，不得决定 status。例：
```tsv
2026-06-10T06:30	c4d5e6f	some-skill	a1b2c3d	3-0-0	keep	失败模式	paired 一致判定 better	paired
```
文件位置：`<skill_root>/results.tsv`

---

## 实战 high-leverage 操作（精髓速查）

4 条经实战验证（image-generation +10.85 / weread-advisor +14.9 / claude-design +16.5）。详细案例数据见 [references/skilllens-evidence.md](references/skilllens-evidence.md) 的「HL 实战案例」节。

- **HL-1（dim4）显性视觉标记是杠杆**：加 🔴 CHECKPOINT / 🛑 STOP，靠「必须」措辞不行——LLM 解析时扫描视觉标记。4 行改动撬动 dim4 +3 分
- **HL-2（dim3）if-then 三段式 fallback 表**：把「症状/解法」两列升级为「触发条件 / 一线修复 / 仍失败兜底」三段式。SkillLens failure-mechanism encoding 维度的落地
- **HL-3（Phase 2 诊断）维度相关簇警告**：dim2/3/4 是相关簇——修 dim3 时 dim2 常跟着涨。「找最大加权短板维度」时同时看相关簇短板再决定是否同步改
- **HL-4（Phase 2 退出）触顶自动 break**：仅统计 kept 轮次；连续 2 轮均是 better 绝对多数，且所有 better 票均为 `margin=slight` → break。无绝对多数直接 review，不计入早停

---

## 优化策略库

按优先级排序，每轮只做最高优先级的一个：

### P0: Runtime 适配性问题（gate 项命中 → 必须先修）
- README/SKILL.md 出现红灯措辞（如「在 Claude Code 里」「Claude Code skill」）→ 替换为 runtime-neutral 措辞
- Badge 钉死单一 runtime → 改为 `Agent Skills Standard` + `skills.sh` + `Multi-Runtime` 三个中立 badge
- 安装章节只给一种 runtime 的路径 → 改为「一行命令（auto-detect）+ 手动路径表 + 作为参考资料」三层结构
- 工作流硬编码 runtime-specific 工具且无 fallback → 给出通用替代方案或标注「仅在某 runtime 可用」
- 例外：skill 名明确标注单 runtime（如 `xxx-codex`）的，可跳过本项

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查skill是否有误导性指令
- 带skill比不带还差 → skill可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确的输出模板

### P1: 结构性问题
- Frontmatter缺少触发词 → 补充中英文触发词
- 缺少Phase/Step结构 → 重组为线性流程
- 缺少用户确认检查点 → 在关键决策处插入

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果X失败，则Y"

### P3: 可读性问题
- 段落过长 → 拆分+用表格
- 重复描述 → 合并去重
- 缺少速查 → 添加TL;DR或决策树

---

## 异常与边界条件

流程假设环境理想，但实操常遇异常。以下预定义 fallback，保证优化过程不会「一跑就卡住」。

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 禁止自动 `git init`；先告知用户将降级为文件备份，修改前创建 `SKILL.md.bak.YYYYMMDD-HHMMSS-r{round}`；若用户要求 Git 棘轮再由其确认初始化仓库 |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行（9列：含 eval_mode） |
| results.tsv 损坏 | 列数不匹配 / 非TSV | 备份为 `.bak.YYYYMMDD-HHMM` 后重建，告知用户 |
| 分支已存在 | `git checkout -b` 失败 | 分支名末尾加 `-2` / `-3`；第3次失败则切回现有分支并询问继续还是新起 |
| `git revert` 失败 | 冲突 / 工作树脏 / `HEAD != candidate_commit` | 停止并告知用户；禁止全局 stash 或覆盖其他文件，仅基于已记录的 candidate/base 处理目标 `SKILL.md` |
| MAX_ROUNDS 触顶（默认3） | 已跑3轮仍有短板 | 不强制 break，展示当前最弱维度问用户「继续加1轮 / 进入Phase 2.5 / 收工」 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，回到改进步骤精简（删冗余/合并重复），再评 |
| test-prompts.json 已存在 | 文件已在 skill 目录 | 默认复用并展示，问用户「复用 / 重写 / 追加」三选一 |
| SKILL.md 找不到 | 目录存在但无 SKILL.md | 该 skill 终止，results.tsv 记 `status=error`，继续下一个 |
| 绝对分浮动 | 不同 judge 的总分不可比 | 总分仅保留 1 位小数用于 triage；keep/revert 只依据 paired 绝对多数决 |

**原则**：异常先告知用户，再按规则处理；绝不静默跳过或静默失败。

---

## darwin 操作反例黑名单（dim9 应用：darwin 自己优化时不要做的事）

来自本机 results.tsv 早期 40 次 0 revert 的教训 + Judge G/H 自指评估暴露的反模式。每条都是**真实踩过的坑**。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | **同 context 自评自改** | 改完后立刻在同一 Claude session 打分，会有「我刚改的肯定更好」乐观偏差（SkillLens 实证 LLM-as-judge 准确率仅 46.4%）| 必须 spawn **独立子 agent**；keep/revert 走 **paired 比较**（同 judge 一次读改前+改后）的**奇数 N 多数决**，**不用绝对分数 delta**（绝对分跨 judge ±8 噪音、不可比） |
| 1b | **拿绝对分数 delta 当 keep/revert 棘轮** | 绝对总分是抽样不是测量；baseline judge 与 rescore judge 用不同「标准尺」，差值大半是换尺、非真实质量变化（实测一支纯加标记的 skill 单评 −8.5、全是换尺）| 绝对分只做 triage 排名；keep/revert 用 paired 多数决，within-judge cancellation 消除换尺污染 |
| 2 | **`git reset --hard` 当回滚** | 会丢工作树未提交改动；CI 历史断裂 | 校验 `HEAD == candidate_commit` 后用 `git revert ${candidate_commit}` 创建反向 commit，保留可追溯链 |
| 3 | **为凑分增冗余** | 触顶后继续硬改往往是「加废话/加段落让 LLM 觉得更详细」，实际质量不变 | 仅统计 kept 轮次；连续 2 轮均是 better 绝对多数且 better 票全为 `slight` → break 进 Phase 3，**见好就收** |
| 4 | **跳过 test-prompts 直接评分** | 没有 test-prompts 的 dim8 是凭空打分，权重 23% 等于编造 | Phase 0.5 强制设计 2-3 prompts；若用户不给，默认编 3 个并展示确认 |
| 5 | **轮内改多个维度** | 多变量同时变，分数升降无法归因到具体改动 | 每轮 1 个维度；相关簇（dim2/3/4）改其一时观察另两个是否跟涨 |
| 6 | **dry_run 比例 > 30%** | dim8 实测维度形同虚设，分数虚高（早期 40 次记录 67% dry_run，0 revert） | 强制至少 1 个真实 full_test；dry_run 多的优化在 results.tsv 显式打 ⚠️ |
| 7 | **静默跳过异常** | 遇到 git/tsv 异常时静默继续，破坏 ratchet 完整性 | 异常表 10 条 fallback 必须先告知用户再处理 |
| 8 | **忽视维度相关性单独优化** | dim2/3/4 是相关簇，单独优化 dim2 时常发现已被前轮 dim3 修复推到顶 | 找最大加权短板维度时同时看相关簇短板，决定是否同步改 |

**触发场景**：每轮 Phase 2 改动前对照本表一次。任一反模式命中 → 改方案重写。

---

## 约束规则

1. **不改变skill的核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不给目标 Skill 引入新依赖** — 不添加目标 skill 原本没有的 scripts、references 或运行时依赖；Darwin 自身的可选成果卡依赖不得注入目标 Skill
3. **每轮只改一个维度** — 避免多个变更导致无法归因
4. **保持文件大小合理** — 优化后SKILL.md不应超过原始大小的150%
5. **尊重原作者风格** — 中文为主、简洁为上
6. **可回滚** — 所有改动在git分支上，用git revert而非reset --hard
7. **评分独立性** — 效果维度必须用子agent或至少干跑验证，不能在同一上下文里「改完直接评」
8. **Runtime 中立性** — skill 必须能在 Claude Code、Codex、Cursor、OpenClaw、Hermes 等任何 skills-compatible runtime 中正常运行。除非 skill 名明确绑定单一 runtime（如 `xxx-codex`、`presentation-workflow-codex`），任何「在 Claude Code 里」「Claude Code skill」「单一 badge 钉死」「安装命令只给 `.claude/skills/` 一种路径」都视为 gate 不通过，须在 P0 优先修复（详见「Runtime 适配性审查」章节）

---

## 使用方式

### 全量优化（推荐首次使用）
```
用户："优化所有skills"
→ Phase 0-3 完整流程
→ 默认：先基线评估，按分数升序优先优化最低 5-10 个
```

### 单个优化
```
用户："优化 presentation-workflow 这个skill"
→ 只对指定skill执行 Phase 0.5-2
```

### 仅评估不改
```
用户："评估所有skills的质量"
→ 只执行 Phase 0.5-1（设计测试prompt + 基线评估），不进入优化循环
```

### 查看历史
```
用户："看看skill优化历史"
→ 读取并展示 results.tsv
```

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本skill的对应关系：
- **program.md** → 本文件（评估rubric和约束规则）
- **train.py** → 每个SKILL.md
- **val_bpb** → ⚠️ **此处是 1.0 的概念错误源**：autoresearch 的 `val_bpb` 是**确定性 loss**（重跑同数），darwin 套到 **LLM-judge 分数（随机抽样）** 上却沿用「绝对值比大小」棘轮 → 不可重复的数当可重复用。修正：9 维 rubric 当 **paired 比较准则**、不当绝对 metric
- **git ratchet** → 仅保留 paired 绝对多数判定 `better` 的 commit（不是「绝对总分更高」的 commit）
- **test set** → 每个skill的test-prompts.json

区别：增加了人在回路（autoresearch是全自主的，skill优化需要人的判断力），以及双重评估机制（结构+效果），因为skill的「好坏」比loss数值更微妙。

### 学术依据 & Credits

- **SkillLens**（arXiv [2605.23899](https://arxiv.org/abs/2605.23899)）：9 维 rubric 的实证来源（LLM 自评 46.4% → 加 meta-skill 三维度后 73.8%）。
- **SkillOpt**（arXiv [2605.23904](https://arxiv.org/abs/2605.23904)）：validation-gated edits 形式化框架。代码 [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)（`pip install skillopt`）、项目页 [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)。🤝 2026-06-03 微软官方仓库已把 darwin-skill 列入集成名单。
- **autoresearch**：[github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)，本 skill 1.0 的原始灵感。

---

## 成果卡片生成（Result Card）

每个skill优化完成后（或全量汇总后），自动生成视觉成果卡片，截图保存为PNG。

### 卡片模板

模板位置：`templates/result-card.html`

3种风格，每次随机选择一种：

| 风格 | CSS类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter字体，干净网格 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 用 sed/编辑工具 替换占位数据：
   - data-field="skill-name" → 实际skill名
   - 默认展示 paired votes / verdict / test results；若模板仍为 score 格式，必须标明「绝对分非 keep/revert 依据」
   - 9个维度的 dim-bar-before/after width 仅用于可选 triage 展示
   - data-field="improvement-1/2/3" → 实际改进摘要
   - data-field="date" → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 若环境已有 Node.js + Playwright/Chromium，用 scripts/screenshot.mjs 截图（2x 高清，只截 .card 元素，自动 open 图片）：
   node "<skill_root>/scripts/screenshot.mjs" \
     /abs/path/to/card.html /abs/path/to/output.png
   # 仅当 npx/playwright 已在本地可用时的回退方案；禁止为生成卡片擅自联网安装：
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 依赖缺失或截图失败时，跳过 PNG，交付 HTML 卡片和文本报告，不得因可选可视化阻断优化结果

### 资源文件速查

| 路径 | 用途 |
|---|---|
| `templates/result-card.html` | 3风格主模板（swiss/terminal/newspaper，hash切换） |
| `templates/result-card-dark.html` / `-white.html` | 单一风格替代模板（需要锁定风格时用） |
| `scripts/screenshot.mjs` | 2x 高清截图，只截 .card，自动 open |
| `results.tsv` | 历次优化日志（9列含 eval_mode） |
| `{skill目录}/test-prompts.json` | 每个 skill 的测试 prompt 集（用于维度8实测） |

### 何时生成

- **单skill卡片**：每个skill优化完成后，展示该skill的分数变化
- **总览卡片**：全部优化完成后（Phase 3），展示全局战绩

### 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill

## 版本自检（仅用户要求时）

默认跳过版本检查。只有用户明确要求检查更新时，才执行本节；禁止因普通优化任务联网或写入 skill 工作树。

用户要求检查更新时：

1. 本目录不是 git 克隆（无 `.git` 或无 origin）→ 报告无法检查并跳过，不写任何文件
2. 默认不联网、不写入 skill 仓库；只有用户明确要求检查更新时，才对比 `git -C <本目录> rev-parse HEAD` 与 `git -C <本目录> ls-remote origin HEAD`
3. 如 runtime 提供 cache 目录，可将检查日期写入 cache；禁止为版本检查污染 skill 工作树
4. 两者一致 → 什么都不说；确认落后 → 先完成用户当前任务，结束后附一句「本 skill 有新版本，可用 `git -C <本目录> pull --ff-only` 更新」。是否更新由用户决定，不要主动执行更新
