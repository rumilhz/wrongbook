# 与其他方案的对比

本文对比 5 类现有"让 Agent 记住教训"的方案，说明本方案（WrongBook）
的定位与取舍。评价标准按用户核心诉求排序：
**能否在"动手写之前"阻止错误发生（前置防错）> token 效率 > 零依赖可移植性**。

---

## 0. 评价维度

| 维度 | 含义 |
|---|---|
| 触发时机 | 常驻（每轮在）/ 被动（检索命中）/ 事后（会话后） |
| 前置防错 | 能否阻止"写之前"的错误——本方案的第一诉求 |
| 存储 | 规则存在哪、怎么管理 |
| 常驻成本 | 每轮固定消耗的 token |
| 依赖 | 是否需要安装外部工具/服务 |

---

## 1. Claude Code 的 CLAUDE.md rules

**机制**：用户（或 Claude 主动询问后）把错误教训写进 `CLAUDE.md`，作为常驻规则；
社区实践者宣称"数月后能捕获项目里所有错误并自动预防"。

| 维度 | 评价 |
|---|---|
| 触发时机 | 常驻 ✅ |
| 前置防错 | 有（方向与本方案一致） |
| 存储 | 规则与项目指令**混存于同一个文件** |
| 常驻成本 | 随规则数量线性上涨 |
| 依赖 | 无 |

**与本方案的差异**：
- 方向一致，但**缺少双层隔离**——规则和指令混在一起，写多了必然膨胀；
- 社区反面案例（dev.to《I Wrote 200 Lines of Rules for Claude Code. It Ignored Them All》）
  证实：单文件堆规则会失效；
- 本方案把"元规则 + ≤5 铁律"与"完整禁则库"拆开，靠元规则触发检索，
  用记忆/lessons.md 承载全部条目。

**结论**：CLAUDE.md rules 是"天然版"的本方案，但没解决膨胀问题。
如果已经在用，只需把"教训类内容"从 CLAUDE.md 迁到独立错题本 + 留一条元规则即可升级。

---

## 2. lessons 数据库类 skill（如 mcpmarket 的 self-improvement-loop）

**机制**：捕获报错 → 写入外部 lessons-learned 数据库（如 SQLite/JSON），
下次相关任务时查询，防止复发。

| 维度 | 评价 |
|---|---|
| 触发时机 | 被动检索 |
| 前置防错 | ❌ ——"写之前"没有查询信号（详见 docs/principle.md §2） |
| 存储 | 外部 DB，需要运行维护 |
| 常驻成本 | 低（不常驻） |
| 依赖 | skill + DB 环境 |

**结论**：本质是"事后记录 + 被动查询"，和记忆系统同构，但没有常驻触发层，
防错效果弱。外部 DB 还增加运维成本——对个人 Agent 属于过度设计。

---

## 3. 事后 lessons 聚合器（如 graphify 的 `reflect` → LESSONS.md）

**机制**：会话结束后把 Q&A 结果聚合生成 LESSONS.md（preferred sources / dead ends），
供下次会话开头阅读。

| 维度 | 评价 |
|---|---|
| 触发时机 | 事后生成，会话开头阅读 |
| 前置防错 | ❌ ——"阅读建议"不等于"写之前强制核对" |
| 存储 | 生成式文档，绑定工具目录结构 |
| 依赖 | 需要安装/运行该工具 |

**结论**：是"回顾报告"不是"防错机制"。适合团队项目复盘，
不适合个人 Agent 的即时防错。

---

## 4. 通用记忆框架（mem0 / MemGPT / Letta / Zep）

**机制**：长期记忆基础设施——语义检索、自主记忆写入、多 Agent 共享记忆等。

| 维度 | 评价 |
|---|---|
| 触发时机 | 语义检索（被动） |
| 前置防错 | ❌（同 §2） |
| 存储 | 向量库 + 服务端 |
| 常驻成本 | 低（不常驻） |
| 依赖 | 重——需要跑服务、管理向量库 |

**结论**：它们是**记忆基础设施**，解决"存很多、找得准"；不是**防错规则层**，
解决"写之前别踩坑"。两者可以组合（用 mem0 存禁则 + 本方案的常驻元规则触发），
但对个人使用是杀鸡用牛刀。

---

## 5. 手动维护的"经验文档"（无结构化机制）

**机制**：把踩坑记录写进项目文档/个人 wiki，想起来就看。

| 维度 | 评价 |
|---|---|
| 触发时机 | 无触发——靠 Agent 自觉想起 |
| 前置防错 | ❌ 完全靠运气 |
| 存储 | 文档 |
| 常驻成本 | 0 |
| 依赖 | 无 |

**结论**：聊胜于无，但"想起来才看"等于没机制。本方案的常驻元规则
解决的就是"自觉性"问题。

---

## 6. 对比总表

| 方案 | 前置防错 | 触发时机 | 常驻成本 | 依赖 | 适合场景 |
|---|---|---|---|---|---|
| **WrongBook（本方案）** | ✅ | 常驻 + 检索 | ~30-60 token/turn | 零 | 个人 Agent 防错，任何平台 |
| CLAUDE.md rules | 半 ✅（膨胀即失效） | 常驻 | 随条目线性涨 | 零 | Claude Code 用户，条目少时 |
| lessons DB skill | ❌ | 被动 | 低 | skill+DB | 团队级错误知识库 |
| graphify 类聚合器 | ❌ | 事后 | 低 | 工具 | 项目复盘 |
| mem0/MemGPT 等 | ❌ | 被动 | 低 | 重（服务） | 大规模记忆需求 |
| 手动经验文档 | ❌ | 无 | 0 | 零 | 没有机制的过渡态 |

---

## 7. 为什么本方案在"省 token"上最优

1. **常驻部分被压到最小**：元规则（~20 token）+ ≤5 条铁律（~40 token），
   每轮固定成本约 30-60 token；
2. **完整禁则库零常驻成本**：只在"写之前检索"或"报错后沉淀"时按需读写；
3. **禁则式单行格式**：每条 20-40 token，比复盘式记录省 3-5 倍；
4. **同类合并**：防止"同一条错记 50 遍"的重复存储。

对比：CLAUDE.md 堆 100 条规则 = 每轮 3000+ token 且失效；
mem0 向量库 = 服务常驻 + 检索延迟；本方案 = 每轮几十 token，无服务。

---

## 8. 参考来源

- dev.to《I Wrote 200 Lines of Rules for Claude Code. It Ignored Them All》
  —— 单文件堆规则的失效案例（https://dev.to/minatoplanb/i-wrote-200-lines-of-rules-for-claude-code-it-ignored-them-all-4639）
- Medium《The Complete Guide to CLAUDE.md: Memory, Rules, Loading, and Cross-Tool Compression》
  —— CLAUDE.md 实践共识（https://medium.com/@bijit211987/the-complete-guide-to-claude-md-memory-rules-loading-and-cross-tool-compression-97cc12ed037b）
- mcpmarket：Self-Improvement Loop (Learn from Errors) skill —— lessons DB 类方案示例
- graphify（work-memory / reflect → LESSONS.md）—— 事后聚合类方案示例
- Reasonix 官方文档《SESSION_MEMORY_RETRIEVAL》—— 指令文件 vs 记忆的加载机制
  （"Instructions are part of the cache-stable prompt prefix；memory is retrieved on demand"）
