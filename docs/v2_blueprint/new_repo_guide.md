# New Repo Guide

更新时间：2026-03-19

## 1. 推荐仓库命名

建议名称：

- `ai-research-os`
- `ai-investment-ops`
- `openclaw-research-core`

如果你希望更强调风控与多 agent，我建议：

- `ai-research-os`

## 2. 本地创建新仓库

假设新仓库放在：

- `/Users/dan/workspace/ai-research-os`

建议命令：

```bash
mkdir -p /Users/dan/workspace/ai-research-os
cd /Users/dan/workspace/ai-research-os
git init
git checkout -b main
```

## 3. GitHub 创建新仓库

推荐步骤：

1. 在 GitHub 创建空仓库，不要勾选 README / .gitignore / license。
2. 本地初始化后再绑定 remote。
3. 使用以下命令：

```bash
git remote add origin git@github.com:<your-org-or-user>/ai-research-os.git
git remote -v
```

## 4. 将模板骨架拷入新仓库

当前工作区已经准备了模板目录：

- `blueprints/ai_research_os_template/`

建议复制方式：

```bash
rsync -av --exclude '__pycache__' --exclude '*.pyc' /Users/dan/cmctestagent/cmctestagent/blueprints/ai_research_os_template/ /Users/dan/workspace/ai-research-os/
```

然后提交第一版：

```bash
cd /Users/dan/workspace/ai-research-os
git add .
git commit -m "chore: bootstrap ai research os skeleton"
```

## 5. 新仓库的第一批目录

模板已经包含：

- `src/ai_research_os/config/`
- `src/ai_research_os/contracts/`
- `src/ai_research_os/runtime/`
- `src/ai_research_os/storage/`
- `src/ai_research_os/agents/`
- `src/ai_research_os/workflows/`
- `migrations/`
- `tests/`

## 6. 推荐分支策略

- `main`
  - 可发布、可演示
- `develop`
  - 可选，如果你想更严格分支管理
- `feature/<name>`
  - 具体功能开发

如果现在只有你和少量协作者，建议直接：

- `main`
- `feature/*`

## 7. 推荐第一批 issue

1. Bootstrap repository skeleton
2. Add SQLite migrations and init command
3. Implement core contracts
4. Implement LLM gateway
5. Implement outbox/task runner
6. Implement Telegram review bot
7. Implement Skill 9 factor pipeline
8. Implement Skill 8 event timeline pipeline

## 8. 新仓库创建后先做什么

按这个顺序：

1. 运行本地环境
2. 初始化 SQLite
3. 补 contracts 测试
4. 打通一个假的 proposal workflow
5. 再接入真实数据源

## 9. 不要一开始做什么

- 不要立刻迁移所有旧 skill
- 不要先接 Web UI
- 不要先接大而全 observability
- 不要先上 Redis / Postgres / LangGraph

## 10. 什么时候可以开始正式开发

当下面 4 个条件满足时，就算真正进入开发期：

- 新仓库已创建
- 模板骨架已复制
- SQLite 初始化可运行
- contracts 已冻结第一版

到这一步，我们就可以开始以 Skill 9 为第一条主链路推进。
