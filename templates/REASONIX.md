# REASONIX.md —— Reasonix 平台专用版（含记忆工具用法）

> 与通用版 AGENTS.md 的差异：Reasonix 原生支持**长期记忆系统**，
> 错题本直接存为全局记忆（每会话索引自动加载 + 正文按需检索），
> 比独立 lessons.md 文件更省 token。本文件放在 Reasonix 用户全局目录
> （如 `%APPDATA%\reasonix\REASONIX.md`），所有项目每轮加载。

## 元规则：写之前先查错题本（防错优先，不做事后纠错）

- 每次执行 bash/PowerShell 命令、写代码、安装包**之前**，先检索全局记忆
  `self-improvement-lessons`（错题本），核对当前操作是否命中禁则；
  命中即用预防性写法，**不等报错再纠错**。
- 命令失败 / exit code 非 0 / 工具报错后：按「禁止 X —— 因为会 Y」格式
  沉淀或扩充错题本，不写长复盘。

## 高频铁律（最痛的 ≤5 条，错题本速览）

- 禁止在 bash 双引号内嵌含 `$_` 的 `powershell -Command "..."` —— 会损坏命令；用单引号包裹或写 `.ps1` 文件。
- 禁止直接 `ls`/操作可能不存在的路径 —— exit 2 判 failed；先 `[ -d p ] &&` 判断。
- 禁止把 MSYS 路径（`/tmp` 等）直接传给 Windows 程序 —— 会报成功但没写文件；先 `cygpath -w` 转换。
- 禁止用未加引号定界符的 heredoc 写含 `\n`/`$` 的内容 —— 会展开变形；用 `<<'EOF'`。

（完整禁则清单在全局记忆 self-improvement-lessons，按需检索；本文件保持精简，新增禁则只进记忆。）

## 记忆工具用法备忘

- **沉淀**：调用记忆工具的 `remember`（type=feedback），一条禁则追加/扩充到
  `self-improvement-lessons`，正文用「禁止 X —— 因为会 Y」格式。
- **检索**：写命令前用记忆工具 `search`（query 含操作关键词，如 `bash`、`exit`、`安装`）
  核对是否命中禁则。
- **主题特定经验**：留在对应主题的记忆里（如部署备忘），错题本只放通用禁则 + `[[链接]]` 指针。
