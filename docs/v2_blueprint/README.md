# V2 Blueprint

这组文档用于支持新仓库的从零重构，目标是把本项目从“脚本化投研系统”升级为“可审核、可学习、可回放的多 agent 投研与风控系统”。

文档说明：

- `architecture_decision.md`
  - 对外部系统设计文档做取舍，给出推荐的 v2 架构与技术栈。
- `development_plan.md`
  - 给出分阶段开发方案、里程碑、验收口径和优先级。
- `phase1_execution_plan.md`
  - 基于已确认约束的 Phase 1 执行版开发文档，包含模块、数据流、SQLite 设计、Discord 交互、Skill 8/9 最小范围、按周 backlog 和验收标准。
- `current_system_inventory.md`
  - 盘点当前仓库里可迁移的数据处理逻辑、API 调用方式和实现经验。
- `new_repo_guide.md`
  - 指导如何创建新仓库，并把模板骨架导入到新仓库中。

配套模板位于：

- `blueprints/ai_research_os_template/`

建议使用方式：

1. 先评审 `architecture_decision.md`，确定 v2 的核心边界。
2. 再评审 `phase1_execution_plan.md`，冻结 Phase 1 执行范围。
3. 按 `new_repo_guide.md` 创建新仓库。
4. 将 `blueprints/ai_research_os_template/` 复制到新仓库作为初始骨架。
5. 按 `development_plan.md` 和 `phase1_execution_plan.md` 进入开发。
