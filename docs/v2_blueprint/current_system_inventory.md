# Current System Inventory

更新时间：2026-03-19

本文档用于记录当前仓库中值得迁移到新仓库的实现经验，避免重构后遗忘既有的数据处理逻辑和 API 调用方法。

## 1. 迁移原则

应该迁移的是：

- 数据源适配经验
- API 调用方式
- 缓存 / 重试 / 降级策略
- 已验证有效的因子逻辑
- 事件时间线与延迟追踪经验
- LLM 网关与结构化输出经验

不建议直接迁移的是：

- 旧的调度入口组织方式
- 旧的 skill 耦合方式
- 旧 repo 的脚本式主流程

## 2. 当前仓库的高价值可迁移模块

### 2.1 LLM Gateway

文件：

- `core/llm_gateway.py`

可迁移点：

- 单一模型网关入口
- 多模型路由
- 结构化 JSON 输出
- provider 级参数降级
- retry/backoff

新仓库建议：

- 保留“统一网关”思想
- 将返回对象绑定到 v2 contracts
- 增加 request cache 和 proposal_id 级成本归集

### 2.2 CoinMarketCap 统一客户端

文件：

- `data_pipeline/cmc_client.py`

现有能力：

- 统一 GET
- 429 / 瞬时错误退避重试
- 本地文件缓存
- 快捷方法：
  - `get_listings`
  - `get_quotes`
  - `get_ohlcv_historical`
  - `get_token_info`
  - `get_fear_and_greed`
  - `get_dex_token`
  - `get_dex_kline`

迁移建议：

- 直接迁移方法设计思路
- 缓存从文件缓存迁到 SQLite `http_cache`
- 为每个 endpoint 补充标准 `Observation` 映射

### 2.3 RSS 底层抓取

文件：

- `data_pipeline/rss_client.py`

现有能力：

- 结构化 `RSSEntry`
- `fetch_feed`
- `fetch_feeds_parallel`
- HTML 清洗
- 时间过滤
- 同步 / 异步双实现

迁移建议：

- 基本可原样迁移
- 输出统一映射为 `Observation`
- 为抓取结果添加 `source_hash` 和 `dedup_key`

### 2.4 RSSHub 路由注册

文件：

- `data_pipeline/rsshub_provider.py`
- `config/rsshub_routes.json`

现有能力：

- 按类别管理 feed
- 支持 keyword route 生成
- 有 healthcheck

迁移建议：

- 保留 registry 思想
- 在新仓库中把类别映射为 `source profile`
- RSSHub 作为中文事件补充源优先保留

### 2.5 Intelligence Hub

文件：

- `data_pipeline/intelligence_hub.py`

现有能力：

- X 搜索摘要
- Tavily 深度搜索
- Newsletter RSS 摘要
- 分类 headlines 聚合

迁移建议：

- 拆成更清晰的 adapter 层：
  - `x_adapter`
  - `tavily_adapter`
  - `rss_digest_adapter`
- 旧仓库返回的是 prompt-friendly string
- 新仓库中应优先输出 `Observation` 或 `EvidencePacket`

### 2.6 加密数据采集与 TA

文件：

- `data_pipeline/crypto_fetcher.py`
- `data_pipeline/ta_engine.py`

现有能力：

- CMC quotes + OHLCV 获取
- Fear & Greed
- CoinMetrics 免费链上指标
- blockchain.info 难度 / 关机币价推演
- RSI / SMA / EMA / MACD 计算

迁移建议：

- TA Engine 可直接迁移
- Crypto fetcher 的“少调用次数覆盖多指标”思想应保留
- 所有指标输出都映射到 `FeatureSnapshot.features`

### 2.7 ResearchBTC 链上数据

文件：

- `data_pipeline/onchain_fetcher.py`

现有能力：

- 异步获取 MVRV / SOPR
- 解析 CSV 风格返回
- graceful degradation

迁移建议：

- 直接保留异步 adapter 设计
- 统一纳入 `OnchainObservation`

### 2.8 OpenBB 轻量补数

文件：

- `data_pipeline/openbb_equity_enricher.py`

现有能力：

- 股票 shortlist 补充信息
- graceful degradation
- 简短 snapshot brief

迁移建议：

- 保留“只做补数，不拖垮主链路”的原则
- 在 v2 中作为 enrichment adapter，而不是 discovery agent

### 2.9 Skill 8：事件时间线与延迟任务

文件：

- `core/event_memory.py`
- `skills/skill_8_blackswan.py`

现有能力：

- SQLite 事件记忆
- `event_timeline`
- delayed phase2 task
- RSS 去重
- 事件升级 / 转变 / 降级
- 两阶段推送

新仓库应重点迁移的不是旧 prompt，而是这些模式：

- 时间线持久化
- 事件状态机
- 延迟深度研究任务
- 新事件 / 重复 / 升级的判定框架

### 2.10 Skill 9：三层漏斗 + 叙事判决

文件：

- `skills/skill_9_altcoin_scanner.py`

现有能力：

- listings 初筛
- OHLCV 获取
- 本地 TA 过滤
- 复合评分
- token metadata 补全
- Grok narrative verdict

新仓库应重点迁移：

- 三层漏斗思想
- 低成本 shortlist 机制
- metadata enrich 逻辑
- 价格与动量因子

不应直接迁移：

- 旧 verdict 直接作为最终结论
- 文本结论大于结构化因子的设计

## 3. 当前仓库的 API 调用方法摘要

### 3.1 CMC

用途：

- 全市场 listings
- latest quotes
- historical ohlcv
- token info
- fear and greed

迁移建议：

- 新仓库统一包成 `adapters/cmc.py`
- 所有方法返回 typed payload

### 3.2 Tavily

用途：

- 深度搜索
- 事件补证

迁移建议：

- 不直接返回大段字符串
- 转为 evidence list

### 3.3 X / Grok

用途：

- KOL / 社媒 / narrative 搜索
- Skill 9 叙事因子来源

迁移建议：

- 新仓库中严格分层：
  - 原始帖子 observation
  - 结构化 narrative factor
  - 最终 decision rationale

### 3.4 RSS / RSSHub

用途：

- 黑天鹅
- 中文产业快讯
- newsletter

迁移建议：

- 优先作为事件输入层，不直接喂给最终 card

## 4. 当前仓库的数据处理逻辑经验

值得保留的工程经验：

- 先过滤，后调用 LLM
- 尽量把 TA 放在本地计算
- 所有外部 API 都要有降级路径
- 结构化输出优先
- 对 LLM 做 prompt 约束和标量归一化

## 5. 新仓库中的迁移优先级

优先迁移：

1. `core/llm_gateway.py`
2. `data_pipeline/cmc_client.py`
3. `data_pipeline/rss_client.py`
4. `data_pipeline/rsshub_provider.py`
5. `data_pipeline/ta_engine.py`
6. `data_pipeline/onchain_fetcher.py`
7. Skill 8 的 timeline 思想
8. Skill 9 的 factor funnel 思想

后迁移：

- OpenBB enrich
- 旧 Telegram bot 的自然语言分析路径
- 其它旧 skill 的具体 prompt

## 6. 新仓库推荐的模块落点

- `adapters/cmc.py`
- `adapters/rss.py`
- `adapters/rsshub.py`
- `adapters/tavily.py`
- `adapters/x.py`
- `adapters/grok.py`
- `adapters/onchain.py`
- `factors/technical.py`
- `factors/narrative.py`
- `factors/risk.py`
- `memory/event_store.py`
- `memory/lesson_store.py`
- `runtime/llm_gateway.py`

这份清单的目的不是复制旧系统，而是确保已验证过的经验不会在重构中丢失。
