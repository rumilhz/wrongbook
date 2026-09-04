# Hooks 强制层（2026-09-02，v0.4 · 5 家 AI 评审收敛版）

> 定位：**hooks 是适配器层，不是产品本体**。核心规则库（`self-improvement-lessons.md`）、
> 外部事件账本（`event-ledger.jsonl`）、审计（`wrongbook-audit.py`）全部平台无关；
> 仅 `scripts/hooks/` 与 `settings.json` 是 Reasonix 专属适配，迁移他平台只换这一层。

## 为什么引入（评审结论）

纯指令防不住"Agent 不执行"（实测核对率 8.2%）。Reasonix 原生 hooks 提供**宿主执行层**，
`PreToolUse` exit 2 是平台级真阻断，不依赖 LLM 自觉。5 家 AI（Gemini/ChatGPT/DeepSeek，
各 2 轮取最优）收敛共识：方向正确，但不构成"纯指令无效"的推翻，而是补一层确定性兜底。

## 事件与职责（四层）

| 事件 | 脚本 | 职责 | 强度 |
|---|---|---|---|
| `SessionStart` | hook-session-start.py | 注入核心禁则**触发词摘要**（≤1500 字符，v2 压缩版） | 弱提醒 |
| `PreToolUse` | hook-pre-tool-use.py | **高危门禁**：5 类正则（rm -rf /、git push --force、curl\|sh、pip --no-verify、mkfs/dd）exit 2 真阻断；仅 cwd 白名单 | 硬强制 |
| `PostToolUseFailure` | hook-post-tool-failure.py | 失败自动写 `event-ledger.jsonl` | 记账 |
| `PostToolUse` | （预留） | 成功事件 → 核对率/exposure 精确来源 | 记账 |

## 三条铁律（评审共识）

1. **raw ledger ≠ 错题库**：`event-ledger` 只是"发生了失败"的原始记录；要沉淀成规则，
   需人工/定期归因抽象（failure → 客观归因 → 六要素规则），绝不把每条失败直接当禁则。
2. **门禁只对高危，不强拦软规则**：`PreToolUse` 只拦截破坏性/不可逆命令（正则机械判定，
   不靠 LLM 判断）；语法/逻辑类软错误走注入提醒，避免误杀正常操作打断工作流。
3. **短超时降级兜底**：门禁 hook `timeout=500ms`，卡住则平台放行（不拖慢所有工具调用）；
   白名单（hooks 脚本目录）豁免正式执行。

## 使用前置

- hooks 需**重启 Reasonix**（或会话内 `/reload`）才加载——配置保存后不立即生效。
- 若误拦合法操作：改白名单（`WHITELIST_DIRS`）或临时移除该 hook 条目。
- 迁移其他 Agent 框架（Claude Code/Codex）：`settings.json` 换 `~/.claude/settings.json`
  hooks 段，同事件名（`PreToolUse`/`SessionStart`/`PostToolUse`），脚本复用。