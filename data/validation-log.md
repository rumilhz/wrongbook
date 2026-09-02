# 验证数据日志（validation log）

> 记录协议见 `docs/validation.md`。三类事件：HIT（前置命中）/ INCIDENT（报错）/ RULE（沉淀）。
> 只记录**可复现、可归因**的事件；一次性环境噪音不记（在 INCIDENT 中注明原因即可）。
> **README 首份验证报告：已于 2026-09-02 回填**（提前于 09-06，见 README「2026-09 首份验证报告」）
> **数据集分层（v0.1，2026-09-02 起）**：本日志按来源分 A(instrumented)/B(historical)/C(external)/D(unattributed)。08-06~09-02 周期事件/规则无 exposure 记录、批量补录未逐日归因，**严谨计为 D 层，不可用于效果 claim**。详见 docs/validation.md §1.5。

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

- [2026-08-13] INCIDENT 命令=（WrongBook 仓库核对任务中）把 `[错题本核对] 领域=命令/Windows 无命中...` 中文标注拼进 PowerShell 命令字符串首行 根因=Windows PS 5.1 将整段当脚本解析：ParserError「表达式或语句中包含意外的标记"领域=命令/Windows"」exit 1，且中文经 GBK 解码变乱码 命中已有禁则=**是**（「禁止把标注/说明文本拼进命令字符串」，2026-08-06 已立）→ **二次复发**（首见于 bash 场景，本次 PowerShell 变体） 沉淀=扩充（禁则标题加 [PowerShell] 域：标注文本只放回复正文，命令串保持纯 ASCII）
- [2026-08-13] RULE 扩充 条目=「[bash/PowerShell] 禁止把标注/说明文本（如 [错题本核对]）拼进 bash/PowerShell 命令字符串」——2026-08-13 二次复发（PS 5.1 ParserError + 中文 GBK 乱码），标题补 PowerShell 域、根因补 PS 5.1 解析行为

- [2026-08-14 ~ 2026-09-02] RULE 区间批量 条目=（**跨会话分散沉淀，validation-log 未逐日同步**——诚实声明：此段 08-14 后多个会话自查触发批量沉淀，只写了全文文件、未同步本日志，无法逐日归因，回填时按区间计）全文文件 `self-improvement-lessons.md` 从 21 → 76 条：净 +55，覆盖 [ffmpeg]/[eval]/[CDP/浏览器]/[解压]/[WebDAV]/[调度] 等领域；含「标注文本」禁则 08-18 三犯、08-21 四犯（PS 内联变体，时间线并入该条禁则，本次一并合并去重 -2）。**教训**：沉淀即时性缺失=记录与实质脱节，2026-09-02 起用 add-lesson 脚本强制「写禁则=记日志」同步。
- [2026-09-02] RULE 修剪 条目=「[bash/PowerShell] 标注文本禁则」——合并 3 变体为 1 条（08-06/08-13/08-18/08-21 时间线合一），全文 78 → 76 条
- [2026-09-02] RULE 文档 回填=README 首份验证报告（周期 08-06 ~ 09-02，提前于 09-06）：observed 3 HIT / 2 regressions（**无 exposure 记录，不报复发率**；早前"40%"表述已按 docs/validation.md §1.5 降级为 absolute observed counts）；命中率因检索次数 T 未记录不统计；08-14~09-02 区间沉淀未逐日归因、计 Dataset D 不可作效果 claim；同日升级沉淀可见仪式 + add-lesson.py
