# 验证数据日志（validation log）

> 记录协议见 `docs/validation.md`。三类事件：HIT（前置命中）/ INCIDENT（报错）/ RULE（沉淀）。
> 只记录**可复现、可归因**的事件；一次性环境噪音不记（在 INCIDENT 中注明原因即可）。

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
- [2026-08-06] RULE 新增 条目=「[脚本/Windows] 禁止在 Python `print` 用 ✓/✗ 等非 GBK 符号 —— 因为 Windows 控制台 GBK 编码抛 UnicodeEncodeError；改用 ASCII 标记 `[OK]`/`[ERROR]`」
