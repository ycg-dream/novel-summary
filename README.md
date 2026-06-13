# novel-summary Skill

> 把任意大小的中文长篇小说 txt 变成结构化摘要的工作流。

切分 → 并行摘要 → 合并,主 Agent 只维护进度笔记与质量校验。

## 适用场景 ✅

- 30 万 ~ 1000 万字的中文长篇小说(网文、轻小说、出版小说均可)
- 想快速回顾剧情但不想重读几百万字
- 需要为长文本训练/研究提供结构化摘要
- 同时跑多本小说(子 Agent 并行,互不干扰)
- 网文中带"加料章"/"车"等 R18 内容,需要智能标记但不复述

## 不适用场景 ❌

- **短篇(< 30 万字)**:用一次普通 LLM 调用更快,不需要切分
- **英文/日文/小语种小说**:本 skill 的提示词和章节匹配针对中文优化
- **图片型/PDF/EPUB**:目前只支持纯文本 `.txt`(如需扩展可贡献 PR)
- **学术论文/技术文档**:走其他摘要方案
- **对"质量 100% 准确"有强需求**:LLM 摘要本质是概率生成,需要人工校对

## 依赖

- **Python 3.8+**(脚本仅用标准库,无第三方依赖)
- **Claude Code / Cursor / VS Code Copilot**(任一支持 Claude Skills 的客户端)
- 子 Agent 推荐模型: **Claude Sonnet 4.6** 或更高(200K 上下文,支持中文长文本)
- 磁盘:每 20 万字切分后约 2-3 MB,合并后单本小说 < 5 MB

## 安装

### 方式 1:作为 Claude Code Skill(推荐)

```bash
# 克隆仓库
git clone https://github.com/yangchanggui1994/novel-summary.git
# 软链到 skills 目录
ln -s "$(pwd)/novel-summary" ~/.claude/skills/novel-summary
```

### 方式 2:作为 Python 工具包

```bash
git clone https://github.com/yangchanggui1994/novel-summary.git
cd novel-summary
# 脚本直接用,无需安装
python diagnose_novel.py --path /path/to/novel.txt
```

## 5 分钟上手

1. **调用 Skill**:对 Claude Code 说"用 novel-summary 这个 Skill 给我读《xxx.txt》"
2. **Skill 自动触发**:Claude 会读 `SKILL.md` 并按工作流执行
3. **提供输入**:小说 txt 路径
4. **第一步:诊断(必做)**:
   ```bash
   python diagnose_novel.py --path /path/to/novel.txt
   ```
   把诊断报告(特别是缺失章节/谐音字/屏蔽词)注入子 Agent 提示词
5. **等待完成**:5-6 个会话 × 30-60 分钟(按 537 万字规模)
6. **清理临时文件(必做)**:
   ```bash
   python cleanup_parts.py
   # 确认删除 (y/N): y
   ```
7. **拿到产物**:单 part 摘要 + 全书汇总

> ⚠️ **不要忘记步骤 4-6**——诊断能避免摘要被"草"="操"等谐音字污染;清理能释放 16MB+ 磁盘。

## 文件结构

```
novel-summary/
├── SKILL.md                  ← 主技能说明(自动加载)
├── README.md                 ← 本文件(人工阅读)
├── CHANGELOG.md              ← 版本变更记录
├── LICENSE                   ← MIT 许可证
├── SKILL_CASE_537W.md        ← 537 万字长篇真实案例
├── _learned_patterns.md      ← 跨书复用经验库(34 主题)
├── diagnose_novel.py         ← 文本质量诊断(切分前必跑)
├── split_novel2.py           ← 切分脚本(UTF-16 编码支持)
├── merge_witch_summaries.py  ← 合并脚本
├── cleanup_parts.py          ← 清理脚本(合并后必跑)
└── templates/
    ├── progress_template.md       ← 进度笔记模板
    └── experience_evaluation.md   ← 经验评估清单
```

> ⚠️ **脚本里的 `WORK_DIR` / `NOVEL_NAME` 等常量是发布者的使用习惯,请按需修改后再跑**(详见脚本内注释)。

## 解决的问题

| 痛点 | 传统做法 | Skill 做法 |
|------|----------|-----------|
| 537 万字读不完 | 主 Agent 串行读 → 上下文爆 | 切 27 段 + 子 Agent 并行 |
| 摘要太水 | 抽取式(jieba) | 生成式(子 Agent 独立读全文) |
| 风格不一致 | 主 Agent 状态波动 | 6 大模块结构化提示词 |
| 加料章处理 | 一刀切 | 提示词明确"标记 ❤ 不复述内容" |
| 跨 part 上下文 | 复制前文摘要 → 提示词爆 | 维护 progress.md 共享已知上下文 |

## 关键参数速查

| 参数 | 推荐值 | 备注 |
|------|--------|------|
| 切分粒度 | **20 万字/段** | 50-65 章/段 |
| 子 Agent 模型 | claude-sonnet-4-6 | 200K 上下文 |
| 摘要字数 | 2000-3000 中文字 | 子 Agent 常写到 4000-5000(接受) |
| 提示词长度 | < 5K token | 避免提示词爆炸 |
| 主 Agent 进度笔记 | < 5K token | 共享已知上下文 |
| 加料章处理 | ❤ 标记,不复述 | 提示词明确强调 |

## 性能基准

| 小说字数 | 切分段数 | 单段字数 | 处理时间 | 清理后体积 |
|----------|----------|----------|----------|------------|
| 30 万字 | 1-2 | 全文 | 5 分钟 | ~10 KB |
| 100 万字 | 5-7 | 15-20 万 | 30 分钟 | ~50 KB |
| 300 万字 | 15-20 | 20 万 | 1-2 小时 | ~200 KB |
| **537 万字** | **27** | **20 万** | **5-6 小时** | **~1 MB** |
| 1000 万字 | 50+ | 20 万 | 10+ 小时 | ~2 MB |

## 完整调用示例

```
用户:帮我用 novel-summary 这个 Skill 读 ~/novels/我的小说.txt,生成全书摘要

Claude:
1. 读 SKILL.md
2. 检测编码 → UTF-8
3. 用 split_novel2.py 切分为 N 个 part
4. 派子 Agent 处理 part 1-4(首批 4 个)
5. 子 Agent 写摘要到 part_001_summary.md ~ part_004_summary.md
6. 主 Agent 校验
7. 用户继续说"继续 part 5-8"
8. 派第二批子 Agent
9. ... 循环直到完成
10. 合并为 全书摘要汇总.md
```

## 输出物格式

每个 part 摘要文件结构:

```markdown
【part_NNN_summary】(约 X 字 / 第 A-B 章)

## 一、核心主线
[200-300 字]

## 二、关键剧情节点
1. **事件名**(章节范围):...
2. ...

## 三、新增人物
- **人物名**:身份/能力/与主角关系

## 四、世界观/设定扩充
1. 设定 1
2. ...

## 五、政治格局变化
1. 变化 1
2. ...

## 六、伏笔/未解线索
1. 伏笔 1
2. ...
```

## 排错快速索引

| 症状 | 原因 | 修复 |
|------|------|------|
| 编码检测说"UTF-8"但实际是 GBK | 头部 4KB 是 ASCII 标题 | 用 multi-offset 检测(已内置) |
| **子 Agent 把"草"=操、"曰"=日 一律解读** | 没看到诊断报告 | **跑 diagnose_novel.py + 把谐音字列表注入提示词** |
| 子 Agent 写"前情回顾" | 没看到"不要写前情" | 在提示词首段加 ⚠️ 警告 |
| 章节摘要把广告/书友群也写进来 | 切分前未清理 | 跑 diagnose 识别,再 Python 切掉 |
| 跨 part 人物名不一致 | 子 Agent 不知道前置 | progress.md 同步更新人物名表 |
| 摘要漏掉缺失章节 | 子 Agent 不知道哪些章节缺失 | **把诊断报告的"缺失章节号"注入提示词** |
| 磁盘占用大(十几 GB) | 合并后忘了清理 part 临时文件 | 运行 `python cleanup_parts.py` 删除 |

详见 `SKILL.md` 排错章节。

## 真实案例

`SKILL_CASE_537W.md` 记录了:
- 实际处理 537 万字《放开那个女巫》小说
- 27 个 part 切分 + 6 大模块摘要
- 4 份 v1 摘要 → 5 份 v2 升级版
- 主 Agent 串行 vs 子 Agent 串行的质量对比
- 性能数据 + 用户反馈

建议阅读。

## 贡献

欢迎提 PR 或 Issue:
- **新经验主题** → 加到 `_learned_patterns.md`(参考归档结构)
- **新小说类型支持**(如玄幻/言情/历史)→ 调整 `SKILL.md` 的提示词模板
- **PDF/EPUB 输入支持** → 扩展 `diagnose_novel.py` 解析层
- **Bug 修复 / 性能优化** → 直接 PR

## 许可证

MIT License,详见 [LICENSE](LICENSE) 文件。

## 反馈

- **Issue**: 在 GitHub 提 issue
- **讨论**: Claude Code Discord / MCP 中文社区
- **星标**: 如果觉得有用,给个 ⭐ 鼓励一下
