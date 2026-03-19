# Phase 1 Execution Plan

更新时间：2026-03-19

## 1. Phase 1 系统边界

### 1.1 目标

在最短时间内跑通一个可验收闭环，而不是先建设重型基础设施平台。

### 1.2 约束

Phase 1 固定采用：

- `SQLite-first`
- `Typed contracts first`
- `Asyncio workers + SQLite-backed durable queue/outbox`
- `Discord-first`
- `Rule-first, LLM-second`
- `低成本、低复杂度、快速闭环优先`

### 1.3 不纳入 Phase 1 的内容

Phase 1 不引入：

- Redis Streams
- PostgreSQL + TimescaleDB
- 对象存储
- 向量库
- LangGraph 作为运行时必选
- 全套 observability stack

### 1.4 Phase 1 必须保留的工程能力

即使不引入重基础设施，也必须保留：

- 事件可追踪
- 状态可恢复
- 人工审核后可继续执行
- 结果可回放
- 输出可评估
- 新版本可对比、可回滚

## 2. Phase 1 核心对象

Phase 1 必须优先稳定以下 typed contracts：

- `Observation`
- `FeatureSnapshot`
- `Hypothesis`
- `DecisionCard`
- `HumanReview`
- `OutcomeRecord`
- `Lesson`
- `EvolutionProposal`

所有关键流程必须携带最小审计字段：

- `proposal_id`
- `trace_id`
- `agent_name`
- `prompt_version`
- `model_name`
- `review_action`
- `outcome_id`

## 3. 模块划分

### 3.1 `contracts`

职责：

- 定义所有 typed contracts
- 控制 schema version
- 约束 agent 间通信对象

Phase 1 必须完成：

- `Observation`
- `FeatureSnapshot`
- `Hypothesis`
- `DecisionCard`
- `HumanReview`
- `OutcomeRecord`
- `Lesson`
- `EvolutionProposal`

### 3.2 `storage`

职责：

- SQLite 初始化
- repository 层
- FTS5 支持
- durable queue 和 outbox
- replay 数据读取

Phase 1 必须完成：

- schema migration
- repository 接口
- outbox / task queue
- state transition logging

### 3.3 `runtime`

职责：

- app bootstrap
- worker scheduler
- checkpoint / resume
- interrupt handling
- replay entrypoint

Phase 1 必须完成：

- async worker runner
- due task scanner
- idempotent consumer
- failure retry

### 3.4 `adapters`

职责：

- 外部 API 接入
- 原始 payload 标准化
- graceful degradation

Phase 1 优先适配：

- RSS / RSSHub
- CMC
- OI / funding / derivatives provider
- Grok / X or equivalent social input
- Discord bot
- Telegram notifier

### 3.5 `factors`

职责：

- 规则筛选
- 技术指标
- narrative factorization
- 风险得分

Phase 1 必须完成：

- Skill 9 因子化
- Skill 8 趋势影响与升级因子

### 3.6 `agents`

Phase 1 只保留最小必要 agent：

- `IngestionAgent`
- `FeatureAgent`
- `Skill9OpportunityAgent`
- `Skill8RiskAgent`
- `CommitteeAgent`
- `ReviewAgent`
- `OutcomeAgent`
- `LearningAgent`

### 3.7 `review`

职责：

- Discord decision card 渲染
- review button / modal handling
- 审核动作落库
- 审核后恢复 workflow

### 3.8 `evaluation`

职责：

- golden set
- failure set
- replay eval
- release gate
- champion / challenger

Phase 1 不要求复杂平台，但必须从第一天开始有目录和接口。

## 4. 数据流

### 4.1 标准 Proposal 流

```text
Observation ingest
-> normalization / dedup
-> feature extraction
-> rule filter / scoring
-> hypothesis generation
-> committee merge
-> DecisionCard generation
-> Discord review delivery
-> HumanReview persist
-> workflow resume
-> outcome tracking tasks created
-> OutcomeRecord generated
-> lesson extraction / evolution input
```

### 4.2 状态机

Phase 1 建议状态：

- `NEW`
- `OBSERVED`
- `FEATURED`
- `RULE_PASSED`
- `HYPOTHESIS_READY`
- `CARD_READY`
- `AWAITING_REVIEW`
- `APPROVED`
- `REJECTED`
- `HOLD`
- `TRACKING`
- `OUTCOME_READY`
- `LESSON_READY`
- `CLOSED`

### 4.3 checkpoint / interrupt / resume 语义

Phase 1 不使用 LangGraph，但必须显式实现：

- `checkpoint`
  - 每个状态变更落库
- `interrupt`
  - 发出 DecisionCard 后进入 `AWAITING_REVIEW`
- `resume`
  - 人类点击审核动作后，worker 继续执行后续步骤
- `replay`
  - 对历史 proposal 重放 feature / hypothesis / scoring

## 5. SQLite 表结构建议

### 5.1 核心业务表

- `observations`
  - 原始 observation
- `observation_fts`
  - observation 文本检索
- `feature_snapshots`
  - 结构化因子快照
- `hypotheses`
  - 研究假设
- `decision_cards`
  - 面向人类审核的卡片
- `human_reviews`
  - 审核动作
- `outcome_records`
  - 后验结果
- `lessons`
  - 提炼的经验
- `evolution_proposals`
  - 新权重 / prompt / threshold 变更提案

### 5.2 工作流与审计表

- `proposal_runs`
  - proposal 主状态机
- `proposal_transitions`
  - 每次状态变更
- `agent_runs`
  - 每个 agent 的执行记录
- `llm_calls`
  - 每次 LLM 调用
- `outbox_events`
  - durable outbox
- `agent_tasks`
  - worker 待执行任务

### 5.3 Skill 8 相关表

- `event_timelines`
  - 黑天鹅事件主表
- `event_timeline_nodes`
  - 时间线节点
- `event_asset_links`
  - 事件与资产映射

### 5.4 Skill 9 相关表

- `signal_factor_snapshots`
  - 多因子截面快照
- `signal_weight_versions`
  - 权重版本
- `signal_tracking_tasks`
  - T+N 跟踪任务

### 5.5 最小字段建议

关键表统一带：

- `proposal_id`
- `trace_id`
- `created_at`
- `updated_at`
- `schema_version`

LLM 表额外带：

- `agent_name`
- `prompt_version`
- `model_name`
- `token_in`
- `token_out`
- `cost_estimate`

Review / outcome 表额外带：

- `review_action`
- `outcome_id`

## 6. Durable Queue 设计

### 6.1 设计目标

必须满足：

- durable
- 可恢复
- 可重试
- 可追踪
- 可幂等

### 6.2 推荐表结构

#### `outbox_events`

字段建议：

- `event_id`
- `topic`
- `payload_json`
- `proposal_id`
- `trace_id`
- `producer_agent`
- `status`
  - `pending|running|done|failed`
- `attempt_count`
- `available_at`
- `last_error`
- `created_at`
- `updated_at`

#### `agent_tasks`

字段建议：

- `task_id`
- `task_type`
- `proposal_id`
- `trace_id`
- `assigned_agent`
- `payload_json`
- `checkpoint_state`
- `status`
  - `pending|running|waiting_human|done|failed`
- `attempt_count`
- `resume_token`
- `available_at`
- `last_error`
- `created_at`
- `updated_at`

### 6.3 worker 语义

worker 循环：

1. 扫描 `available_at <= now`
2. claim 一批 pending task
3. 更新为 running
4. 执行
5. 写入 checkpoint
6. 成功则 done
7. 失败则 backoff retry
8. 若需人工审核则转 `waiting_human`

### 6.4 interrupt / resume 机制

当 ReviewAgent 发出 DecisionCard 后：

- `agent_tasks.status = waiting_human`
- 写入 `resume_token`
- 记录 `checkpoint_state = AWAITING_REVIEW`

当 Discord 回调到达时：

- 插入 `human_reviews`
- 找到对应 `resume_token`
- 新建或恢复 `agent_task`
- 从 `AWAITING_REVIEW` 继续执行

### 6.5 replay 机制

Phase 1 replay 不要求复杂图引擎，只要做到：

- 根据 `proposal_id` 读取完整输入
- 重新运行 feature / scoring / hypothesis / card generation
- 对比 champion / challenger 输出

## 7. Discord 交互设计

### 7.1 为什么 Discord-first

原因：

- 频道适合按场景拆分：
  - `#skill8-risk`
  - `#skill9-opportunities`
  - `#review-queue`
  - `#approved-ideas`
- thread 适合把单个 proposal 的证据、追踪和复盘串在一起
- component API 适合 button、select menu、modal

### 7.2 Decision Card 结构

建议一张卡包含：

- 标题
- action
- 一句话 thesis
- why now
- top evidence 3 条
- key risks 2 条
- trigger / invalidation
- confidence
- 审计摘要
  - `proposal_id`
  - `agent_name`
  - `prompt_version`
  - `model_name`

### 7.3 审核动作

必须支持：

- `Approve`
- `Reject`
- `Edit and Approve`
- `Hold`
- `Need More Evidence`
- `Mark Lesson`

### 7.4 拒绝原因标签

建议提供快速选择：

- `evidence_insufficient`
- `timing_wrong`
- `macro_conflict`
- `crowded_trade`
- `risk_not_covered`
- `wrong_mapping`
- `derivatives_overheated`
- `narrative_unconvincing`
- `poor_rr`

### 7.5 Telegram 的 Phase 1 定位

Telegram 只做：

- 高优先级黑天鹅提醒
- Discord 审核卡片的兜底通知
- 移动端摘要提醒

不作为主审核入口。

## 8. Skill 9 在 Phase 1 的最小实现范围

### 8.1 目标

在最短时间内跑通：

- 数据输入
- 规则筛选 / 因子化
- LLM 辅助生成 DecisionCard
- Discord 审核
- Outcome 跟踪

### 8.2 必做输入

- CMC listings / quotes / OHLCV
- 一个 derivatives 数据源
  - OI
  - funding
  - liquidation 或 basis 二选一即可
- 一个社媒 / narrative 输入源
  - Grok 或 X 搜索摘要

### 8.3 必做因子

- `trend`
  - EMA、RSI、MACD、量价
- `derivatives`
  - OI delta
  - funding regime
  - liquidation pressure
- `official_or_narrative`
  - official_update_score
  - kol_consensus_score
  - narrative_velocity_score
- `risk_penalty`
  - crowded_trade_penalty
  - liquidity_penalty

### 8.4 不在 Phase 1 强求

- 全量链上覆盖
- regime-aware 自适应多权重引擎
- 自动权重上线
- 多模型辩论

### 8.5 最小输出

- shortlist
- factor snapshot
- hypothesis
- decision card
- T+1 / T+3 / T+7 / T+14 tracking task

## 9. Skill 8 在 Phase 1 的最小实现范围

### 9.1 目标

跑通：

- 事件发现
- 去重
- timeline
- 风险卡片
- Discord 审核
- 后验跟踪

### 9.2 必做输入

- RSS
- RSSHub
- Tavily 或等价搜索补证
- 基础市场确认
  - 价格
  - 波动
  - 相关资产共振

### 9.3 必做能力

- 事件去重
- EventTimeline 持久化
- `trend_impact_score`
- `human_escalation_score`
- 风险建议追踪

### 9.4 不在 Phase 1 强求

- GraphRAG
- 因果图谱
- 多阶段复杂推演图
- 黑天鹅全市场自动联动分析平台

### 9.5 最小输出

- event timeline
- risk hypothesis
- decision card
- T+1 / T+3 / T+7 / T+14 outcome tracking

## 10. Phase 1 backlog

### Week 1

- 冻结 contracts v1
- 建 SQLite schema v1
- 建 migration / init 命令
- 建 outbox / agent_tasks / proposal_runs
- 建最小 app bootstrap

### Week 2

- 建 Discord bot skeleton
- 建 DecisionCard renderer
- 建 HumanReview callback flow
- 建 checkpoint / resume 流程
- 建审计字段贯通

### Week 3

- 接入 CMC adapter
- 接入 RSS / RSSHub adapter
- 接入基础 LLM gateway
- 建 FeatureAgent
- 建 Skill 9 基础规则筛选

### Week 4

- 建 Skill 9 narrative factorization
- 建 CommitteeAgent
- 建 Skill 9 DecisionCard 生成
- 跑通 Discord review -> resume

### Week 5

- 建 Skill 8 事件去重与 timeline
- 建 trend_impact_score
- 建 human_escalation_score
- 建 Skill 8 风险卡片

### Week 6

- 建 OutcomeAgent
- 自动创建 T+N tracking task
- 生成 OutcomeRecord
- 初版 Lesson 提取

### Week 7

- 建 `golden_set_core`
- 建 `failure_set_recent`
- 建 replay eval CLI
- 建 champion / challenger 接口

### Week 8

- 做端到端回放
- 做 release gate
- 修复稳定性问题
- 冻结 Phase 1 验收版本

## 11. 评估与验收标准

### 11.1 从第一天开始必须存在

- `golden_set_core`
- `failure_set_recent`
- `replay_eval`
- `release_gate`
- `champion_challenger` 预留接口

### 11.2 验收标准

Phase 1 通过验收，至少满足：

- 任一 proposal 都能通过 `proposal_id` 和 `trace_id` 完整追踪
- Discord 审核动作能驱动 workflow 恢复执行
- 系统重启后未完成任务不会丢失
- Skill 9 能形成一条完整机会闭环
- Skill 8 能形成一条完整风险闭环
- 每条已审核提案都能生成 OutcomeRecord
- replay 能对 champion / challenger 做输出对比
- release gate 能阻止未通过验证的新版本进入默认路径

### 11.3 最低成功信号

只要下面这些能跑通，Phase 1 就是成功的：

- 有真实 DecisionCard 在 Discord 中被人审核
- 审核结果落库
- 后续价格表现被跟踪
- OutcomeRecord 进入下一轮评估

## 12. 升级到 Phase 2 的触发条件

满足以下条件中的多数，再进入 Phase 2：

- Skill 8 / Skill 9 闭环稳定运行至少 2-4 周
- replay eval 已形成固定节奏
- champion / challenger 已开始产生真实差异
- SQLite outbox 在吞吐或并发上接近瓶颈
- 需要多 worker / 多进程扩展
- 需要更复杂的 interrupt / resume 图式流程
- 需要更强的多人协作和分析查询能力

## 13. Phase 2 升级方向

当触发条件成立时，再评估：

- Redis Streams
- PostgreSQL / TimescaleDB
- LangGraph
- 更完整 observability
- 对象存储
- 向量检索

结论：

Phase 1 的核心不是把系统做重，而是把“可审核、可追踪、可回放、可比较、可进化”的主闭环做实。只要这个闭环稳定，后续升级到底座层会顺很多。
