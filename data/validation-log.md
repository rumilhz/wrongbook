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

- [2026-08-13] INCIDENT 命令=（排查"弹窗 cmd"任务前 4 次只读 bash 调用：`find`/`tasklist`/`schtasks`/`reg query`） 根因=只读/排查类命令未写 `[错题本核对]` 行，被用户问「错题本你用了吗」当场抓包 命中已有禁则=**是**（「禁止对检查/验证/只读类命令豁免核对」，2026-08-06 已立）→ **二次复发** 沉淀=扩充（注记：多步任务从第一次 bash 调用起每条都写核对行，任务前半段的排查/只读阶段最容易漏）
- [2026-08-13] INCIDENT 命令=（用户提供他处案例：启动文件夹 `ollama-serve.cmd` 中文注释乱码） 根因=无 BOM UTF-8 中文 `.cmd` 的 `rem` 注释被 cmd 按 GBK 解析成乱码，注释文本被当命令执行报「'8-12锛?set' 不是内部或外部命令」 命中已有禁则=否（关联「无 BOM UTF-8 中文 .ps1」禁则，同因变体） 沉淀=扩充（.cmd/.bat/.vbs 启动脚本一律纯 ASCII）
- [2026-08-13] RULE 扩充 条目=「[Reasonix] 禁止对检查/验证/只读类命令豁免错题本核对」——2026-08-13 二次复发（前 4 次只读 bash 漏核对行被抓），加注记
- [2026-08-13] RULE 新增 条目=「[bash/Windows] 禁止用 bash 会话启动需跨调用存活的常驻进程（`ollama serve` 等）—— 因为调用结束清理整棵进程组：`Start-Process`/`wscript` 拉起的进程同一条命令内验证是活的、下一条命令 `PROCESS_GONE`；常驻服务 VBS 放启动文件夹由 explorer 启动」
- [2026-08-13] RULE 扩充 条目=「[PowerShell/Windows] 禁止写无 BOM UTF-8 中文脚本」——加 `.cmd`/`.bat` 变体（rem 注释 GBK 乱码被当命令执行）
- [2026-08-13] HIT  领域=bash 禁则=「heredoc 定界符避开内容中的 `<<'EOF'` 字样」 效果=写记忆文件改用 `<<'WRITEMEMEOF'` 定界符 避错=1
- [2026-08-13] HIT  领域=bash 禁则=「不直接操作可能不存在的路径」 效果=多处先 `[ -f ] &&` 判断再 cat/ls 避错=1
- [2026-08-13] HIT  领域=bash/PowerShell 禁则=「`$_` 用单引号包裹」 效果=进程查询整串单引号包裹防 bash 展开 避错=1
