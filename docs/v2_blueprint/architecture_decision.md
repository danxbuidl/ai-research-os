# V2 Architecture Decision

更新时间：2026-03-19

## 1. 结论

外部设计文档的总体方向是正确的：

- 多 agent
- AI proposes, human verifies
- 可追溯的 Decision Card / Review / Outcome / Lesson 闭环
- Skill 8 / Skill 9 的持续学习
- 生产推理与离线进化分离

但它对 v1 的基础设施设计偏重。对于一个从零重构、需要尽快跑通闭环且严格控制复杂度和成本的新仓库，我建议采用：

- `SQLite-first`
- `Typed contracts first`
- `Asyncio + SQLite durable queue`
- `Discord-first`
- `Rule-first, LLM-second`

而不是一开始就采用：

- Redis Streams
- PostgreSQL + TimescaleDB
- LangGraph 作为必选运行时
- Object store / vector store / full observability stack 全量上齐

## 2. 推荐的 v2 目标形态

v2 的第一目标不是“多 agent 数量多”，而是先跑通一个稳定的生产闭环：

1. 数据进入系统
2. 结构化因子生成
3. Opportunity / Risk 两类 agent 产出提案
4. Committee 汇总成 Decision Card
5. 人类低负担审核
6. 结果追踪
7. Lesson 与权重更新

只有这 7 步跑顺，后续的自治、更多 agent、更多数据源才有意义。

## 3. 推荐技术栈

### 3.1 运行时

- Python 3.12
- `asyncio`
- `httpx`
- `pydantic`
- `litellm`
- `APScheduler`

说明：

- `APScheduler` 只负责定时发现和补偿任务。
- 真正的链路推进通过 SQLite 中的任务状态和 outbox 驱动。

### 3.2 主存储

强制推荐：

- `sqlite3`
- `JSON1`
- `FTS5`

原因：

- 依赖最小
- 足够支撑 v1 的提案、审核、结果、经验、事件时间线
- 便于本地回放、审计、备份和迁移

不建议在 v1 就把生产主链路放到 PostgreSQL + TimescaleDB。

### 3.3 事件驱动方式

推荐：

- SQLite `outbox_events`
- SQLite `agent_tasks`
- 本地 async workers

不推荐：

- Redis Streams 作为 v1 必选

原因：

- Redis 适合更大规模并发和多进程消费。
- 当前 v1 关键矛盾不是吞吐，而是决策闭环、可恢复性和架构清晰度。
- 先把 durable queue 和 replay 模式在 SQLite 跑顺，之后若吞吐变高再外迁到 Redis。

### 3.4 工作流编排

推荐：

- 自建轻量状态机
- 每个 proposal 拥有显式状态
- 每个状态转换落库

暂不推荐：

- LangGraph 作为 v1 运行时依赖

原因：

- LangGraph 很适合复杂 HITL 和长流程恢复，但会把 v1 的认知成本抬高。
- 当前更需要稳定的数据契约、清晰的状态转移和可回放表结构。
- 未来如出现跨天研究流、复杂中断恢复、多个研究分支，再评估引入 LangGraph。

### 3.5 检索与记忆

推荐：

- SQLite FTS5 用于新闻、事件、lesson 检索
- 结构化历史样本优先于向量检索

暂不推荐：

- mem0 / Zep / GraphRAG / Graphiti 作为 v1 生产主能力

原因：

- Skill 8 / Skill 9 的第一阶段更需要“结构化回放”和“历史同类样本对比”，而不是重型图记忆系统。
- 历史案例、事件时间线、OutcomeRecord 已足够构成 v1 的学习基底。

### 3.6 观测与成本

v1 推荐：

- 应用日志
- SQLite `llm_calls`
- SQLite `agent_runs`
- 每 proposal 的 token/cost 归集

v1 不强制：

- OpenTelemetry
- Tempo / Jaeger
- Prometheus

这些可以在 v2.2 以后补。

### 3.7 交互层

Phase 1 明确推荐：

- `Discord-first`
- `Telegram-second`

原因：

- Discord 更适合多 agent 输出的频道化和线程化组织。
- Button、select menu、modal 等交互组件更适合审核流。
- thread 比 Telegram 更适合保留一条 proposal 的完整上下文。
- Telegram 在 Phase 1 更适合高优先级提醒和移动端兜底通知。

## 4. 推荐 agent 拓扑

不要一开始就上 20 个 agent。推荐用 8 个核心 agent 即可：

1. `IngestionAgent`
   - 抓取 Observation。
2. `NormalizationAgent`
   - 标准化 Observation，做去重、打标签。
3. `FeatureAgent`
   - 生成 `FeatureSnapshot`。
4. `CryptoOpportunityAgent`
   - Skill 9 主研究链路。
5. `BlackSwanRiskAgent`
   - Skill 8 主风险链路。
6. `CommitteeAgent`
   - 合并机会与风险视角，生成统一结论。
7. `ReviewDeliveryAgent`
   - 生成并发送 Decision Card，接收 HumanReview。
   - Phase 1 以 Discord 为主，Telegram 为高优先级提醒。
8. `LearningAgent`
   - 生成 Outcome / Lesson / EvolutionProposal。

## 5. 推荐的数据契约

新仓库 v1 必须优先稳定以下对象：

- `Observation`
- `FeatureSnapshot`
- `Hypothesis`
- `RiskAssessment`
- `DecisionCard`
- `HumanReview`
- `OutcomeRecord`
- `Lesson`
- `EvolutionProposal`

原因：

- 这是所有 agent 协作的关节。
- 只要这些对象稳定，后续替换数据源、模型和策略都不会破坏系统主骨架。

## 6. SQLite 表设计建议

v1 核心表建议：

- `observations`
- `observation_fts`
- `feature_snapshots`
- `hypotheses`
- `risk_assessments`
- `decision_cards`
- `human_reviews`
- `investment_memos`
- `outcome_records`
- `lessons`
- `weight_versions`
- `prompt_versions`
- `evolution_proposals`
- `agent_runs`
- `llm_calls`
- `outbox_events`
- `agent_tasks`
- `event_timelines`
- `event_links`

## 7. Skill 9 设计决策

Skill 9 在 v1 中应优先完成以下闭环：

1. 多源 observation 接入
2. 因子化
3. 机会评分
4. Risk veto
5. Decision Card
6. T+N 结果追踪
7. 因子权重离线更新

因子族建议固定为：

- `trend`
- `derivatives`
- `onchain`
- `official`
- `social_kol`
- `market_view`
- `risk_penalty`

Grok 或其它模型生成的官方动态 / KOL 观点 / 市场讨论，必须拆成结构化字段，例如：

- `official_update_score`
- `official_update_type`
- `kol_bullish_score`
- `kol_bearish_score`
- `kol_consensus_score`
- `narrative_velocity_score`
- `narrative_divergence_score`
- `market_view_alignment_score`
- `credibility_weight`

## 8. Skill 8 设计决策

Skill 8 在 v1 中应优先完成以下闭环：

1. 事件去重
2. EventTimeline 持久化
3. Trend Impact Score
4. Human Escalation Score
5. 决策建议后的资产追踪
6. Lesson 提炼

事件系统中必须区分：

- 事件是否发生
- 事件是否可信
- 事件是否足以影响趋势
- 事件是否需要人类介入

## 9. LLM 成本决策

生产链路必须严格分层：

- `Layer A`
  - 无模型：规则、阈值、TA、打分、过滤
- `Layer B`
  - 低成本模型：抽取、分类、结构化
- `Layer C`
  - 中成本模型：候选排序解释、Decision Card
- `Layer D`
  - 高成本模型：Top-K Memo、黑天鹅推演

默认原则：

- 全量扫描不上高成本模型
- 相同证据包只压缩一次
- 只对 shortlist 做深度研究
- 每个 agent 有预算上限

## 10. 何时再升级技术栈

满足以下任一条件，再考虑引入 Redis / Postgres / LangGraph：

- 多 worker 并发和 backlog 明显超出单机 SQLite 能力
- 单条 proposal 存在复杂多分支恢复需求
- 需要跨进程消费同一事件流
- 需要更强的在线分析能力
- 需要复杂协作面板和多研究员并发

结论：

v2 的最佳落地方案不是“最大化技术栈”，而是“最小化不可逆复杂度”。先用轻底座把 Discord Review、Outcome、Lesson 和 replay 跑通，再演进成更重的生产系统。
