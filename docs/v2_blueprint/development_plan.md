# V2 Development Plan

更新时间：2026-03-19

## 1. 开发顺序

推荐顺序：

1. 先稳定 contracts 和 SQLite schema
2. 再搭运行时骨架
3. 再做 Discord review 闭环
4. 再做 Skill 9 最小闭环
5. 再做 Skill 8 风险闭环
6. 最后做学习与进化

不要反过来从“多 agent 编排框架”开始。

## 2. Phase 0：设计冻结与脚手架

目标：

- 冻结核心对象
- 初始化仓库
- 落地 SQLite schema
- 落地基础目录结构

交付物：

- `Observation` / `DecisionCard` / `HumanReview` / `OutcomeRecord` 契约
- `Lesson` / `EvolutionProposal` 契约
- `migrations/0001_init.sql`
- `runtime/`、`storage/`、`agents/`、`workflows/` 骨架
- `.env.example`
- 本地启动入口

验收标准：

- 项目可以本地启动
- SQLite 初始化成功
- 基础测试通过

## 3. Phase 1：Proposal 最小闭环

目标：

- 跑通一个 proposal 从 Observation 到 HumanReview 的完整链路

推荐只做：

- `IngestionAgent`
- `FeatureAgent`
- `CryptoOpportunityAgent`
- `CommitteeAgent`
- `ReviewDeliveryAgent`

交付物：

- observation 入库
- feature snapshot 生成
- hypothesis 生成
- decision card 生成
- Discord review 组件交互
- human review 落库

验收标准：

- 人可以在 Discord 上 approve / reject / hold
- 每个 proposal 有完整 trace
- 失败重试不会重复发卡
- 人工审核后 workflow 能恢复执行

## 4. Phase 2：Skill 9 正式闭环

目标：

- 完成 Altcoin 扫描、因子化、风险约束和结果追踪

交付物：

- 价格动量因子
- OI / funding / basis / liquidation 因子接口
- 官方动态 / KOL / 市场观点因子化
- Risk veto
- OutcomeRecord 跟踪任务

验收标准：

- 每条 Skill 9 建议都能追溯到因子快照
- 每条建议都能追踪 T+1/T+3/T+7/T+14
- 人类 reason tags 能回流到 lesson 流程

## 5. Phase 3：Skill 8 正式闭环

目标：

- 完成黑天鹅事件时间线、趋势影响判断和人类升级机制

交付物：

- EventTimeline
- Trend Impact Score
- Human Escalation Score
- 黑天鹅建议结果追踪
- 历史事件相似检索

验收标准：

- 同一事件不会重复告警泛滥
- 每个重大事件都有 timeline
- 每条风险建议都能回放后验结果

## 6. Phase 4：Learning Loop

目标：

- 让系统具备真正的“可进化”能力

交付物：

- Outcome Attribution
- Lesson extraction
- weight versioning
- prompt versioning
- evolution proposal
- replay evaluator

验收标准：

- 新权重必须先通过 replay
- 新 prompt 必须先走 challenger
- 人类可以批准或拒绝 evolution proposal

## 7. 第一批任务拆分建议

### 7.1 基础设施

- 建 SQLite schema
- 建 settings
- 建 outbox/task runner
- 建 llm gateway

### 7.2 契约层

- 建 Pydantic contracts
- 建 schema versioning
- 建 serialization helpers

### 7.3 Discord 交互层

- 发卡片
- 接收 review
- reason tag 按钮
- more evidence / hold 流程

### 7.4 Skill 9

- 迁移 CMC client
- 接 OI/funding 数据源
- 做 feature adapters
- 做 scorer
- 做 review card

### 7.5 Skill 8

- 迁移 RSS / RSSHub / Tavily / 事件时间线逻辑
- 做 impact score
- 做 escalation score
- 做风险卡片

## 8. Definition of Done

一个功能只有同时满足以下条件才算完成：

- 有契约定义
- 有数据库表或持久化路径
- 有测试
- 有日志
- 有失败恢复
- 有文档

## 9. 不要提前做的内容

- GraphRAG
- 自由辩论式多 agent
- 大而全 Web Console
- 在线自动改 prompt
- 一次性把所有旧 skill 全部迁走

## 10. 推荐节奏

- 第 1 周：contracts + storage + runtime skeleton
- 第 2 周：Discord review bot + proposal workflow
- 第 3-4 周：Skill 9 最小闭环
- 第 5-6 周：Skill 8 闭环
- 第 7-8 周：Outcome / Lesson / Evolution

先把两条最有价值链路做深，再扩面。
