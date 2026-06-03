# Obsidian Codex Memory 后续优化规划

项目当前已经解决了 Codex 缺乏长期记忆、重复介绍项目、上下文无法跨设备同步的问题。后续优化方向不应该盲目增加复杂功能，而是围绕两个目标展开：

- 让 AI 更快理解项目
- 进一步减少 token 消耗

## 第一阶段：Project Summary

Project Summary 是项目摘要系统。当前版本已加入基础命令：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py project-summary
```

它会从 `Codex/Codex 会话总结.md` 生成 `Codex/project-summary.md`，作为 Codex 启动时优先读取的低 token 项目上下文。

后续继续增强摘要质量。

插件从记忆库中提炼：

- 项目名称
- 项目目标
- 技术栈
- 当前进度
- 已完成任务
- 待办事项
- 重要技术决策

生成简洁的 `project-summary.md`。Codex 启动时优先读取摘要，而不是读取全部记忆，从而减少上下文长度并提升理解速度。

## 第二阶段：Memory 分类体系

将记忆按照不同类别管理，而不是把所有内容堆在一个文件中。

建议分类：

- Project
- Decision
- Todo
- Bug
- User Preference

这样既方便用户查看，也方便 AI 精准读取相关内容。

## 第三阶段：Decision Log

实现 Decision Log，也就是决策记录系统。

重点记录“为什么这样做”，而不是只记录“做了什么”。例如：

- 为什么选择某个框架
- 为什么放弃某个方案
- 为什么修改架构
- 为什么保留某个限制

这类信息通常比聊天记录更有长期价值。

## 第四阶段：自动摘要与归档

对历史记忆自动进行压缩总结，将大量低价值聊天记录转换成高价值知识点，避免记忆库无限膨胀。

目标是把数千甚至上万 token 的历史内容压缩为几百 token 的核心信息。

## 第五阶段：记忆质量优化

增加记忆质量优化机制：

- 重复内容检测
- 相似记忆合并
- 重要性评分，也就是 Importance Score
- 高价值记忆优先保留和读取
- 低价值记忆自动降权或归档

## 第六阶段：Generate Context

增加 Generate Context 功能。

一键生成适合 Codex、Claude Code、Cursor 等 AI 编程工具读取的标准项目上下文文件，内容包括：

- 项目简介
- 技术栈
- 当前状态
- 待办事项
- 关键决策
- 近期变更

该功能应成为插件的核心亮点。

## 长期规划

长期再考虑：

- MCP
- 多 Agent 共享记忆
- 跨平台 AI 生态支持

这些功能优先级低于摘要、分类、决策记录和上下文生成。

## 核心原则

1. Markdown 优先，而非数据库优先。
2. 用户可读、可编辑、可控制。
3. 优先提升用户体验，而非追求技术复杂度。
4. 目标不是构建最复杂的 Memory System，而是构建最易用的 AI 第二大脑。
5. 所有功能都应围绕“让 AI 在最少 token 消耗下最快理解项目”这一核心目标展开。
