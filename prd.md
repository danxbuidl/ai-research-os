# AI-Native 多 Agent 投研与风控系统系统设计文档（重构版）

版本：v2.0  
日期：2026-03-19  
定位：从零重构、面向 Phase 1 快速闭环与可持续演进的系统设计文档

---

## 1. 文档目的

本文档定义一个**从零重构**的、面向投研与风险控制的 AI-Native 多 Agent 协作系统。

本版本相较于前版的核心变化是：

- 不以“先搭重基础设施平台”为目标
- 以“**尽快跑通可验收闭环**”为第一优先级
- 采用 **Lean Runtime** 作为 Phase 1 架构画像
- 保留 AI agent 工程必须具备的：
  - typed contracts
  - checkpoint 语义
  - 人工审核
  - 结果追踪
  - 评估闭环
  - 版本放行与回滚

系统目标不是自动下单，而是将跨资产、跨来源的市场与事件信息，转化为**可审核、可追溯、可评估、可进化**的交易建议与投资备忘录。

---

## 2. 总体结论与设计主张

### 2.1 本版设计主张

本系统在 Phase 1 采用以下原则：

- **SQLite-first**
- **Typed contracts first**
- **Asyncio workers + SQLite-backed durable queue/outbox**
- **Discord-first**
- **Rule-first, LLM-second**
- **Low complexity, low cost, fast validation first**

### 2.2 为什么这样设计

对于一个从零开始的新仓库，首要目标不是先做成一个完备的平台，而是：

1. 先跑通一个完整的人机共驾闭环
2. 先形成可评估、可复盘的数据资产
3. 先建立版本验收机制
4. 再在瓶颈明确之后升级基础设施

因此，Phase 1 **不强制**引入以下组件：

- Redis Streams
- PostgreSQL + TimescaleDB
- LangGraph 作为必选运行时
- object store
- vector store
- full observability stack

但必须保留它们所解决的关键语义：

- 事件可追踪
- 状态可恢复
- 人工审核后可继续执行
- 结果可回放
- 输出可评估
- 新版本可对比、可回滚

---

## 3. 目标与非目标

### 3.1 目标

1. 构建一个事件驱动的多 Agent 投研系统，替代传统脚本拼接。
2. 支持低负担的人类审核：AI 提案，人类快速判断、补充或否决。
3. 支持 Skill 9 的 Altcoin 因子化扫描、结果追踪、权重迭代。
4. 支持 Skill 8 的黑天鹅时间线、趋势影响判断、升级人工审核和学习闭环。
5. 从第一天开始建设 Golden Set、Failure Set、Replay Eval 和 Release Gate。
6. 让未来升级到 Redis / Postgres / Timescale / 更强运行时成为平滑迁移，而不是推倒重来。

### 3.2 非目标

1. 不做实盘自动下单。
2. 不做高频执行系统。
3. 不做首版全栈平台化建设。
4. 不让生产环境中的 Agent 自动修改线上核心逻辑并立即生效。
5. 不在 Phase 1 引入 GraphRAG、全局自治辩论、多层知识存储。

---

## 4. 设计原则

### 4.1 决策原则

- **AI Proposes, Human Verifies**：AI 给出提案与理由，人类决定是否采用。
- **Rule-first, LLM-second**：规则与因子优先，LLM 用于压缩、解释、排序和辅助判断。
- **Typed Contracts over Free-form Chat**：Agent 间通过结构化对象协作。
- **Replay before Evolution**：任何进化必须先通过离线回放和评估。
- **Evidence before Opinion**：推荐必须绑定证据、风险与失效条件。
- **Lean first, scale later**：先做轻量闭环，再升级基础设施。

### 4.2 工程原则

- **单机优先，语义不缩水**
- **状态外置，流程可恢复**
- **最小依赖，最大可验收性**
- **先做可运行，再做可扩展，再做高并发**
- **所有关键链路必须可追踪、可回放、可评估**

---

## 5. 系统边界与对外交互

### 5.1 系统定位

系统是一个以 Discord 为主交互层的投研 Agent 操作系统，服务对象是单人或小团队研究/交易决策流程。

### 5.2 对外产出

系统只对外输出两类对象：

1. **Decision Card（决策卡）**
   - 面向即时审核
   - 在 Discord 中展示

2. **Investment Memo（投资备忘录）**
   - 面向归档、复盘、经验沉淀
   - 在提案审核通过后生成

### 5.3 人类动作

人类对任何提案可执行：

- Approve
- Reject
- Edit and Approve
- Hold
- Need More Evidence
- Save as Lesson

所有动作必须持久化。

### 5.4 为什么 Discord-first

Phase 1 采用 Discord 作为主交互媒介，原因：

- 更适合多 agent 协作形态
- 便于按主题/agent/事件拆分频道与线程
- 更适合提案线程、讨论上下文、补充证据与多人协作
- 审核按钮、命令式交互和结构化讨论更自然

Telegram 可保留为高优先级提醒与移动端兜底通知通道，但不是主交互平面。

---

## 6. Phase 1 总体架构（Lean Runtime）

### 6.1 架构目标

在不引入重型基础设施的前提下，提供以下能力：

- 事件 ingestion
- 因子化
- 提案生成
- 风险审核
- Discord 人审
- 审核后继续执行
- 结果追踪
- 经验提炼
- 离线评估

### 6.2 架构分层

```text
┌────────────────────────────────────────────┐
│            Discord Interaction Layer       │
│ Channels / Threads / Commands / Review UI  │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│         Proposal & Review Workflow Layer   │
│ Committee / Decision Card / Human Review   │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│            Research & Risk Agent Layer     │
│ Skill 8 / Skill 9 / Theme / Macro / Risk   │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          Feature & Signal Processing Layer │
│ Rules / Scoring / Factorization / Ranking  │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│           Local Durable Runtime Layer      │
│ Asyncio Workers + SQLite Queue / State DB  │
└────────────────────────────────────────────┘
```

### 6.3 Phase 1 技术画像

| 领域 | 选型 |
|---|---|
| 主数据库 | SQLite |
| 队列 | SQLite-backed durable queue / outbox |
| Worker 模型 | Asyncio workers |
| 交互层 | Discord |
| 报告生成 | 本地 Markdown / SQLite 索引 |
| 结构化模型 | Pydantic |
| 日志 | 文件日志 + SQLite 审计表 |
| 评估 | 本地 eval runner + SQLite / JSONL 数据集 |
| 通知兜底 | Telegram（可选） |

### 6.4 Phase 2 预留升级方向

仅在出现明确瓶颈时升级到：

- Redis Streams
- PostgreSQL + TimescaleDB
- 更强 workflow runtime
- object store
- richer observability
- vector store

---

## 7. 核心数据契约（Typed Contracts）

Phase 1 最重要的工程任务之一，是先稳定以下 typed contracts。

### 7.1 Observation

```json
{
  "observation_id": "obs_...",
  "source_type": "rss|x|discord|cmc|coinglass|defillama|manual",
  "source_ref": "...",
  "entity_refs": ["BTC", "SOL", "AI_THEME"],
  "event_time": "2026-03-19T09:40:00Z",
  "ingested_at": "2026-03-19T09:40:15Z",
  "content_type": "news|social|metric|ohlcv|macro|onchain|derivatives",
  "payload": {}
}
```

### 7.2 FeatureSnapshot

```json
{
  "snapshot_id": "fs_...",
  "entity_type": "asset|theme|event|macro_regime",
  "entity_ref": "SOL",
  "as_of": "2026-03-19T10:00:00Z",
  "features": {}
}
```

### 7.3 Hypothesis

```json
{
  "hypothesis_id": "hyp_...",
  "hypothesis_type": "buy_bias|watch|avoid|reduce|event_risk",
  "entity_refs": ["SOL"],
  "time_horizon": "swing|position|event",
  "thesis": "...",
  "supporting_evidence_refs": ["ev_1"],
  "risk_refs": ["risk_1"],
  "confidence": 0.72,
  "generated_by": "skill9_altcoin_agent",
  "generated_at": "2026-03-19T10:03:22Z"
}
```

### 7.4 DecisionCard

```json
{
  "decision_card_id": "dc_...",
  "title": "SOL 突破后回踩确认候选",
  "entity_refs": ["SOL"],
  "action": "buy_bias",
  "summary": "...",
  "why_now": "...",
  "top_evidence": ["...", "...", "..."],
  "key_risks": ["...", "..."],
  "trigger_conditions": ["突破并站稳 ..."],
  "invalidation_conditions": ["跌回 ... 以下"],
  "confidence": 0.68,
  "needs_human_review": true,
  "review_actions": ["approve", "reject", "edit", "hold", "more_evidence"]
}
```

### 7.5 HumanReview

```json
{
  "review_id": "hr_...",
  "decision_card_id": "dc_...",
  "reviewer": "lucas",
  "action": "reject",
  "reason_tags": ["too_early", "weak_follow_through"],
  "free_text": "逻辑成立，但追价太早",
  "edited_fields": {},
  "reviewed_at": "2026-03-19T10:05:10Z"
}
```

### 7.6 OutcomeRecord

```json
{
  "outcome_id": "out_...",
  "decision_card_id": "dc_...",
  "entity_ref": "SOL",
  "horizon": "T+7",
  "return_pct": 0.082,
  "max_drawdown_pct": -0.031,
  "hit_trigger": true,
  "hit_invalidation": false,
  "evaluated_at": "2026-03-26T00:00:00Z"
}
```

### 7.7 Lesson

```json
{
  "lesson_id": "les_...",
  "source_review_id": "hr_...",
  "lesson_type": "timing|risk|evidence|factor|mapping",
  "lesson_text": "OI 未确认时，叙事驱动的 Altcoin 提案默认降级一档",
  "scope": "skill9_altcoin_agent",
  "status": "candidate|approved|deprecated"
}
```

### 7.8 EvolutionProposal

```json
{
  "evolution_proposal_id": "ep_...",
  "target_scope": "skill9_altcoin_agent",
  "proposal_type": "factor_weight_update|prompt_update|threshold_update|workflow_update",
  "proposal_payload": {},
  "based_on_eval_run": "eval_...",
  "status": "candidate|approved|rejected|shadow",
  "approved_by": null
}
```

---

## 8. 本地 Durable Runtime 设计

### 8.1 设计目标

不用 Redis 也要具备以下语义：

- durable queue
- at-least-once delivery
- 幂等处理
- 失败重试
- dead letter
- replay
- workflow 状态恢复

### 8.2 核心实现方式

采用：

- `SQLite state DB`
- `SQLite queue/outbox table`
- `Asyncio workers`
- `claim -> process -> ack` 模式

### 8.3 Queue 表建议字段

- `job_id`
- `job_type`
- `payload_json`
- `status`（pending / claimed / done / failed / dead_letter）
- `attempt_count`
- `max_attempts`
- `available_at`
- `claimed_by`
- `claimed_at`
- `acked_at`
- `correlation_id`
- `causation_id`
- `idempotency_key`
- `created_at`
- `updated_at`

### 8.4 Workflow State 表建议字段

- `workflow_id`
- `workflow_type`
- `current_state`
- `state_payload_json`
- `awaiting_human_review`
- `last_checkpoint_at`
- `resumable_token`
- `created_at`
- `updated_at`

### 8.5 Checkpoint 语义

即使不引入 LangGraph，Phase 1 也必须保留：

- step-level state persistence
- interrupt for human review
- review 后 resume
- replay by workflow_id
- rollback to prior checkpoint

实现方式可以是：

- 每个关键节点后写入 workflow_state
- 在 `awaiting_human_review = true` 时挂起
- review 到达后生成 resume job

---

## 9. Agent 拓扑设计

### 9.1 Agent 分类

#### A. 数据与输入 Agent

1. **Market Data Agent**
2. **Derivatives Data Agent**
3. **Onchain Data Agent**
4. **News/Social Ingestion Agent**
5. **Macro Data Agent**

#### B. 特征与筛选 Agent

6. **Feature Extraction Agent**
7. **Universe Filter Agent**
8. **Signal Scoring Agent**

#### C. 研究与风险 Agent

9. **Skill 9 Altcoin Agent**
10. **Skill 8 Black Swan Agent**
11. **Theme Research Agent**
12. **Macro Regime Agent**
13. **Risk Veto Agent**
14. **Committee Agent**
15. **Decision Card Agent**

#### D. 学习与治理 Agent

16. **Outcome Attribution Agent**
17. **Review Summarizer Agent**
18. **Reflection Agent**

### 9.2 Agent 边界原则

- 只通过 typed contracts 协作
- 不允许自由文本直接作为上下游 API
- 任何结论必须经过 Committee / Decision Card 收敛
- Risk Veto Agent 拥有风险覆盖权
- Reflection Agent 只能产出 EvolutionProposal，不能直接修改生产配置

---

## 10. Phase 1 核心业务闭环

### 10.1 最小闭环

Phase 1 必须先跑通如下闭环：

1. 数据输入
2. Observation 生成
3. FeatureSnapshot 生成
4. 规则筛选 / 因子化
5. Hypothesis 生成
6. DecisionCard 生成
7. Discord 人审
8. HumanReview 落库
9. OutcomeRecord 追踪
10. Lesson / EvolutionProposal 生成

### 10.2 标准状态机

- `NEW`
- `OBSERVED`
- `FEATURED`
- `SCORED`
- `HYPOTHESIS_READY`
- `DECISION_READY`
- `AWAITING_HUMAN_REVIEW`
- `APPROVED`
- `REJECTED`
- `ON_HOLD`
- `OUTCOME_PENDING`
- `OUTCOME_RECORDED`
- `LESSON_EXTRACTED`

### 10.3 人工审核后的恢复

- Approve -> 生成 memo + 开始 outcome tracking
- Reject -> 写入 review + 进入 lesson candidate
- Edit and Approve -> 更新 decision card + 记录 edited fields + 开始 tracking
- Need More Evidence -> 重新发起补充 research job
- Hold -> 暂停并等待后续触发

---

## 11. Skill 9（每日 Altcoin 扫描）专项设计

### 11.1 目标

Skill 9 是一个高频日度 Altcoin 机会发现与跟踪子系统。目标不是简单扫涨跌，而是：

- 接入多源数据
- 将输入全部因子化
- 生成 buy/watch/avoid 信号
- 在信号后持续追踪结果
- 基于结果迭代因子权重
- 人类批准后再影响下一轮判断

### 11.2 输入数据范围

1. 现货行情
2. 成交量与相对强弱
3. OI
4. OI 变化率
5. Funding Rate
6. Basis
7. 多空比
8. 爆仓分布
9. 交易所净流入/流出
10. 活跃地址/聪明钱行为
11. 官方动态
12. KOL 观点
13. 市场叙事与情绪
14. 解锁、上所、合作、产品更新等事件

### 11.3 因子组设计

#### A. 价格与动量因子
- 1D / 3D / 7D / 14D 相对收益
- 相对 BTC / ETH 强弱
- 波动率压缩/扩张
- 趋势突破/回踩确认

#### B. 合约结构因子
- OI 分位数
- OI 与价格是否同向共振
- OI 背离强度
- Funding 极值
- Basis 异常
- 爆仓区域接近度

#### C. 链上因子
- 交易所净流入/流出
- 巨鲸活跃度
- 聪明钱共识度
- 活跃地址变化

#### D. 叙事因子
- `official_update_score`
- `official_update_type`
- `kol_bullish_score`
- `kol_bearish_score`
- `kol_consensus_score`
- `narrative_velocity_score`
- `narrative_divergence_score`
- `market_view_alignment_score`
- `credibility_weight`

#### E. 事件与基本面因子
- 解锁风险
- 上所/下所事件
- 供给变化
- 合作/发布/路线图兑现
- 流动性改善/恶化

### 11.4 Grok / 观点数据如何因子化

任何来自模型整理的官方动态、KOL 和市场观点，必须落成结构化字段，不允许只保留自然语言摘要。

目标是让这些信息进入：

- FeatureSnapshot
- replay eval
- 因子权重学习
- failure attribution

### 11.5 信号后结果追踪

每个 Skill 9 提案必须创建 outcome tracking：

- T+1
- T+3
- T+7
- T+14
- T+30

记录：

- return_pct
- max_drawdown_pct
- trigger 是否触发
- invalidation 是否触发
- OI/Funding/成交/叙事后续如何演化
- 是否被黑天鹅或宏观 regime 打断

### 11.6 权重迭代机制

Skill 9 的权重更新流程：

1. Reflection Agent 拉取历史提案与 OutcomeRecord
2. 按市场 regime、币种类别、叙事类型分桶分析
3. 生成新的因子权重/阈值候选
4. 在 golden set 和 replay 上验证
5. 生成为 EvolutionProposal
6. 人类审批通过后生效

**禁止自动直接改线上权重。**

### 11.7 人类审核标签

建议预置：

- narrative_unconvincing
- derivatives_overheated
- oi_not_confirming
- weak_follow_through
- too_early
- liquidity_risk
- crowded_trade
- poor_rr

---

## 12. Skill 8（黑天鹅警告）专项设计

### 12.1 目标

Skill 8 不只是一次性发警报，而是一个：

- 事件检测
- 时间线维护
- 趋势影响判断
- 人工升级判断
- 结果追踪
- 经验学习

的完整风险系统。

### 12.2 EventTimeline 设计

每个黑天鹅事件建立独立时间线：

- 首次发现时间
- 事件类型
- 初始可信度
- 关键发展节点
- 官方确认/否认节点
- 风险扩散节点
- 风险缓解节点
- 结束或转常态监控节点

### 12.3 建议后的资产追踪

每次 Skill 8 建议（规避、减仓、等待、左侧观察等）后，必须对受影响资产做结果追踪：

- T+1 / T+3 / T+7 / T+14 / T+30
- 是否形成趋势段
- 是否快速修复
- 是否二次冲击
- 不同资产敏感度差异

### 12.4 Trend Impact Score

判断事件是否会造成趋势化价格影响，建议由以下维度综合：

1. 事件强度
2. 影响范围
3. 持续时间预期
4. 可验证性
5. 市场脆弱性
6. 价格/成交/OI 是否确认
7. 历史相似事件映射

### 12.5 Human Escalation Score

判断是否必须人工介入：

- Trend Impact Score 高
- 事件可信但市场反应分歧大
- 建议涉及大幅风险暴露调整
- 与当前宏观判断冲突
- 证据不完整但传播速度快
- 同类历史事件误判率高

### 12.6 学习闭环

1. 建立 EventTimeline
2. 记录每次建议与后续表现
3. Outcome Attribution Agent 做误差归因
4. Reflection Agent 生成阈值/模板/升级规则调整建议
5. 人类审批后更新下一版 Skill 8

### 12.7 黑天鹅历史库

按以下维度结构化：

- 事件类别
- 影响资产范围
- 首报到主趋势段时间差
- 最大冲击幅度
- 是否二次冲击
- 最佳处理动作
- 误判案例

---

## 13. Discord 交互设计

### 13.1 交互目标

让系统在 Discord 中呈现为“多 agent 协作式研究工作台”，而不是简单通知机器人。

### 13.2 建议的频道结构

- `#market-ops`
- `#skill9-altcoin-scan`
- `#skill8-black-swan`
- `#theme-research`
- `#human-review`
- `#approved-memos`
- `#eval-and-reflection`

### 13.3 线程策略

每次提案或重大事件创建独立 thread：

- 便于 agent 补充证据
- 便于人类 review
- 便于后续 outcome 更新
- 便于回溯全过程

### 13.4 Decision Card 交互内容

每张卡片应展示：

- 标题
- 动作建议
- 一句话 thesis
- why now
- 三条证据
- 两条风险
- trigger
- invalidation
- confidence
- 查看详情 / 查看时间线 / 查看证据按钮
- 审核按钮

### 13.5 审核动作

- Approve
- Reject
- Edit
- Hold
- Need More Evidence
- Save as Lesson

---

## 14. SQLite 数据模型设计

### 14.1 核心表

- `observations`
- `feature_snapshots`
- `hypotheses`
- `decision_cards`
- `human_reviews`
- `outcome_records`
- `lessons`
- `evolution_proposals`
- `event_timelines`
- `event_timeline_nodes`
- `workflow_states`
- `job_queue`
- `agent_runs`
- `llm_calls`
- `audit_log`

### 14.2 `job_queue` 表

用于 durable queue。

### 14.3 `workflow_states` 表

用于 checkpoint 语义。

### 14.4 `llm_calls` 表

最小字段：

- `call_id`
- `proposal_id`
- `agent_name`
- `model_name`
- `prompt_version`
- `input_ref`
- `output_ref`
- `token_in`
- `token_out`
- `cost_estimate`
- `created_at`

### 14.5 `audit_log` 表

最小字段：

- `trace_id`
- `proposal_id`
- `event_type`
- `actor`
- `payload_ref`
- `created_at`

---

## 15. LLM 使用与成本控制

### 15.1 总原则

- 规则优先
- LLM 只用于高杠杆步骤
- 高成本模型只服务于高价值提案
- 同一证据包只总结一次

### 15.2 模型层级

#### Layer A：无模型层
- 数据清洗
- 因子计算
- 阈值判断
- 排序预筛选

#### Layer B：低成本模型层
- 文本分类
- 结构化抽取
- 官方动态/KOL 因子化
- 风险标签生成

#### Layer C：中成本模型层
- 提案压缩
- why now 解释
- decision card 生成
- 风险理由组织

#### Layer D：高成本模型层
- 仅用于少数高价值 memo 或重大黑天鹅双边情景分析

### 15.3 成本治理

必须实现：

- 每 proposal 成本归因
- prompt_version 记录
- 缓存
- Top-K 限流
- 模型 fallback
- 每 agent 预算

---

## 16. EvalOps 与验收门设计

### 16.1 评估原则

- checkpoint 不等于质量达标
- 必须从第一天开始建设 eval
- 模块级评估与端到端评估并行
- 失败样本优先
- 任何升级必须经过 challenger 流程

### 16.2 数据集分层

- `golden_set_core`
- `golden_set_shadow`
- `failure_set_recent`
- `drift_set_live`

### 16.3 Evaluator 分层

- Rule-based evaluator
- LLM-as-judge evaluator
- Human annotation evaluator
- Outcome-based evaluator

### 16.4 Skill 9 评估重点

- 因子抽取正确率
- 官方动态/KOL 因子化一致率
- OI/Funding/Basis 结构因子准确率
- precision@k
- ranking NDCG
- buy/watch/avoid 合理性
- outcome calibration

### 16.5 Skill 8 评估重点

- 事件分类准确率
- 时间线节点完整率
- Trend Impact Score 准确率
- escalation recall / precision
- 假警报率
- 风险解除误判率

### 16.6 Release Gate

任一 challenger 上线前必须满足：

1. schema 合法率过线
2. golden set_core 过线
3. failure_set_recent 不回归
4. 成本不超预算
5. 人类审批通过

### 16.7 Champion / Challenger

- champion：生产版本
- challenger：候选版本
- 先 offline eval
- 再 shadow run
- 再人工批准
- 最后切换

---

## 17. Phase 1 交付范围

### 17.1 必做

1. SQLite schema
2. Asyncio worker runtime
3. SQLite durable queue
4. Workflow state persistence
5. Discord Review Bot
6. Skill 9 最小可用版
7. Skill 8 最小可用版
8. DecisionCard 生成
9. HumanReview 落库
10. Outcome tracking
11. Golden set / failure set 初版
12. Eval runner 初版

### 17.2 不做

1. Redis Streams
2. Postgres / Timescale
3. Object store
4. Vector store
5. GraphRAG
6. 多模型自治辩论
7. 完整 Web Console

---

## 18. Phase 1 验收标准

系统只有在满足以下条件时才算通过 Phase 1：

1. 至少一个完整业务闭环跑通
2. Discord 中可完成审核与继续执行
3. Skill 9 能完成因子化、提案、追踪
4. Skill 8 能完成时间线、风险建议、追踪
5. OutcomeRecord 能自动生成
6. golden_set_core 已建立并可运行
7. challenger 能通过离线评估流程
8. 所有关键链路有最小审计记录

---

## 19. 升级到 Phase 2 的触发条件

当出现以下情况之一，再升级基础设施：

1. 多 agent 并发显著增加
2. fan-out / 多消费者需求变强
3. SQLite 写入成为瓶颈
4. outcome / feature 时序数据量快速膨胀
5. 单机 replay / shadow run 开始吃力
6. 需要更强的 workflow durability 与调度能力

升级方向：

- Redis Streams
- PostgreSQL + TimescaleDB
- 更强 workflow runtime
- richer observability
- object store / vector store

---

## 20. 最终总结

这份设计文档的核心不是“先做一个重平台”，而是：

**先做一个轻量但完整的 AI agent 闭环系统。**

它必须从第一天就具备：

- typed contracts
- checkpoint 语义
- human review
- outcome tracking
- golden set
- release gate
- replay eval
- champion / challenger

但不必从第一天就引入全部复杂基础设施。

因此，本系统的正确路径是：

**Lean Runtime Phase 1 -> Scalable Platform Phase 2**

而不是：

**Heavy Platform First -> 再考虑业务闭环**

这也是本版本文档的核心设计结论。

