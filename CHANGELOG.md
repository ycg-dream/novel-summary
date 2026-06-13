# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-14

### Added
- 首次公开发布
- 核心工作流:切分 → 子 Agent 并行摘要 → 合并
- 4 个 Python 工具脚本:
  - `diagnose_novel.py` — 文本质量诊断(编码/谐音字/缺失章节检测)
  - `split_novel2.py` — 按 20 万字/段切分(支持 UTF-8/UTF-16/GBK)
  - `merge_witch_summaries.py` — 合并所有 part 摘要
  - `cleanup_parts.py` — 清理切分临时文件
- 2 个 templates:
  - `progress_template.md` — 主 Agent 进度笔记模板
  - `experience_evaluation.md` — 经验评估清单
- 6 大模块结构化摘要提示词(核心主线/关键节点/新增人物/世界观/政治格局/伏笔)
- R18 内容三级处理策略(标记 ❤ / 不复述 / 不影响剧情因果链)
- 真实案例文档 `SKILL_CASE_537W.md`(537 万字《放开那个女巫》实战)
- 跨书复用经验库 `_learned_patterns.md`(34 主题)

### Notes
- 本版本基于 537 万字长篇实战经验沉淀
- 配套客户端:Claude Code / Cursor / VS Code Copilot
- 推荐子 Agent 模型:Claude Sonnet 4.6(200K 上下文)
