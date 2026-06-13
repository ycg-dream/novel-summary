# 贡献指南

感谢你考虑为 novel-summary 贡献!无论你是修 typo、加新小说类型支持,还是优化提示词,都欢迎。

## 行为准则

- 友好、尊重、专业
- 反馈基于事实而非个人偏好
- 接受建设性批评,以协作心态改进

## 我能贡献什么

### 1. 修 Bug / 优化现有功能
- 切分脚本边界条件(`split_novel2.py`)
- 编码检测逻辑(`diagnose_novel.py`)
- 合并脚本处理空 part / 缺摘要

### 2. 适配新小说类型
- 玄幻 / 言情 / 历史 / 科幻 / 同人 等
- 修改 `SKILL.md` 里的提示词模板
- 调整 6 大模块的内容偏向

### 3. 扩展输入格式
- PDF / EPUB / DOCX 解析支持
- 扩展 `diagnose_novel.py` 的输入层

### 4. 沉淀新经验主题
- 把"做某本小说时学到的通用方法"加到 `_learned_patterns.md`
- 格式参考现有 🔴🟡🟢 三档结构
- 避免主题平铺堆叠(每个主题 ≤ 1 页)

### 5. 文档改进
- README 错别字 / 翻译 / 截图
- `SKILL.md` 工作流补充场景
- 排错索引 `排错快速索引` 表补行

## 我**不**适合贡献什么(免得 PR 被拒)

- ❌ 硬编码用户个人小说 / 文件路径
- ❌ 引入第三方依赖(本 skill 仅用 Python 标准库)
- ❌ 替换主流程为单一 LLM 调用(会失去"切分+并行"的核心优势)
- ❌ 加料章"完整复述"(违反平台规则,见 SKILL.md 加料章处理)

## 提 PR 流程

1. **Fork** 本仓库
2. 在你 fork 里建分支:`git checkout -b fix-xxx` 或 `feat-xxx`
3. 修改 + 提交(commit message 用中文,简短说明)
4. **测试**:
   - Python 脚本改动:跑 `python diagnose_novel.py --path tests/sample.txt` 不报错
   - 提示词改动:在 Claude Code 里实际跑一次小规模(< 50 万字)小说
   - 文档改动:在 GitHub Preview 确认渲染正常
5. **推 PR** 到 `main` 分支,标题用中文,正文说明:
   - 改了什么
   - 为什么改
   - 怎么测试的
6. 等待 review,通常 1-3 天内回复

## 提 Issue 流程

按 `.github/ISSUE_TEMPLATE/` 下的模板填:
- 🐛 **Bug 报告** —— 程序报错 / 切分错位 / 编码检测错
- 💡 **功能请求** —— 想要支持 PDF / 加新小说类型
- 📚 **新经验主题** —— 沉淀 `_learned_patterns.md` 内容

## 提交频率建议

- **小修小补**(typo / 排版):随时提 PR
- **功能改动**(加新小说类型):先开 issue 讨论,避免方向不一致
- **架构改动**(改主流程):必须先开 RFC issue 讨论

## 联系

- **GitHub Issue**: 在本仓库提
- **讨论区**: Claude Code Discord / MCP 中文社区

## 许可证

贡献的代码按 MIT 协议授权,与本项目主仓库一致。
