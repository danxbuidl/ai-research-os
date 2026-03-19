# AI Research OS Template

这是新仓库的最小骨架模板，目标是支持：

- 多 agent 投研与风控系统
- SQLite-first 持久化
- Typed contracts
- Discord-first 审核流
- Review / Outcome / Lesson / EvolutionProposal 闭环
- Asyncio workers + SQLite durable queue

推荐初始化顺序：

1. 配置 `.env`
2. 安装依赖
3. 初始化 SQLite
4. 跑通 contracts 和 storage 测试
5. 跑通 Discord review 最小闭环
6. 再接真实数据源和 Skill 8 / Skill 9

目录说明：

- `src/ai_research_os/config/`
  - 环境配置
- `src/ai_research_os/contracts/`
  - 跨 agent 的核心对象
- `src/ai_research_os/runtime/`
  - 应用启动、任务总线、工作流调度
- `src/ai_research_os/storage/`
  - SQLite 初始化与 repository
- `src/ai_research_os/agents/`
  - agent 抽象与注册
- `src/ai_research_os/review/`
  - Discord review 交互骨架
- `src/ai_research_os/evaluation/`
  - golden set / replay / challenger 入口
- `src/ai_research_os/workflows/`
  - proposal / review / outcome workflow
- `migrations/`
  - SQLite schema

Phase 1 模板重点：

- 显式 `proposal_id` / `trace_id`
- 审计字段贯通
- `waiting_human` / `resume_token` 语义
- `golden_set_core` / `failure_set_recent` / `replay_eval` / `release_gate` 预留接口

下一步建议：

- 先实现 `DecisionCard`、`HumanReview` 和 Discord 审核恢复执行的最小闭环。
