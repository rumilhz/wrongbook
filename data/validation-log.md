# 验证数据日志（validation log）

> 记录协议见 `docs/validation.md`。三类事件：HIT（前置命中）/ INCIDENT（报错）/ RULE（沉淀）。
> 只记录**可复现、可归因**的事件；一次性环境噪音不记（在 INCIDENT 中注明原因即可）。
> **下次回填 README 验证报告：2026-09-06**（满 4 周）

## 基线（2026-08-06 启动）

- 错题本条目：9 条
- 累计：HIT 0 ｜ INCIDENT 0 ｜ RULE 0
- 常驻成本：全局指令文件 12 行，约 <60 token/轮

---

## 事件记录

<!-- 按日期追加，格式：
- [YYYY-MM-DD] HIT  领域=… 禁则=「…」 效果=… 避错=1
- [YYYY-MM-DD] INCIDENT 命令=… 根因=… 命中已有禁则=是/否 沉淀=新增/扩充/不沉淀（原因）
- [YYYY-MM-DD] RULE 新增/扩充/修剪 条目=「禁止 X —— 因为会 Y」
-->

- [2026-08-06] INCIDENT 命令=`python scripts/validate_lessons.py`（首跑） 根因=`print("✓")` 中 U+2713 在 Windows GBK 控制台抛 UnicodeEncodeError 命中已有禁则=否（关联「UTF-8 编码保中文输出」，同类变体） 沉淀=新增
- [2026-08-06] INCIDENT 命令=`python scripts/validate_lessons.py README.en.md` 根因=RULE_RE 只认中文「禁止」且 `DON'T\S` 不匹配"空格+内容"（英文条目被漏判） 命中已有禁则=否 沉淀=扩充（校验脚本支持双语：`DON'T` + em dash 根因标记）
- [2026-08-06] INCIDENT 命令=（示范核对时）把 `[错题本核对] ...` 文本拼进 bash 命令字符串 根因=bash 把标注当命令执行：command not found exit 127 + 含 `<<'EOF'` 触发 heredoc 解析错乱 命中已有禁则=否 沉淀=新增（禁则：标注文本放回复正文，不进命令字符串）
- [2026-08-06] RULE 新增 条目=「[bash] 禁止把标注/说明文本（如 [错题本核对]）拼进 bash 命令字符串 —— 因为 command not found exit 127 + heredoc 解析错乱；放命令之前的回复正文」
- [2026-08-06] RULE 新增 条目=「[脚本/Windows] 禁止在 Python `print` 用 ✓/✗ 等非 GBK 符号 —— 因为 Windows 控制台 GBK 编码抛 UnicodeEncodeError；改用 ASCII 标记 `[OK]`/`[ERROR]`」
