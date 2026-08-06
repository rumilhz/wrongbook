#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验错题本（lessons）文件格式 —— 防错本身的防错。

规则：
1. 每条禁则以 `- [领域] 禁止 ...` 开头（领域非空）；续行必须缩进
2. 每条禁则必须含根因标记 `—— 因为`
3. 规范化首句后查重（同一条错记两遍 = 冗余）
4. 条目数 > MAX_RULES 时输出修剪提醒（warning，不失败）

用法：
    python scripts/validate_lessons.py <file-or-glob>...
示例：
    python scripts/validate_lessons.py templates/lessons.md templates/lessons.seed.md
退出码：0 = 通过；1 = 存在格式错误（warning 不导致失败）
"""
import re
import sys
from pathlib import Path

MAX_RULES = 100  # 超过此数量提醒修剪（防止清单膨胀失效）

RULE_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\s*((?:禁止|DON'T).*)$", re.IGNORECASE)
CONT_RE = re.compile(r"^\s{2,}\S.*$")  # 缩进续行
ROOT_CAUSE_ZH = "——"      # 中文根因标记
ROOT_CAUSE_EN = "—"        # 英文根因标记（em dash）

def has_root_cause(full: str) -> bool:
    """根因标记：中文「—— 因为」或英文 em dash（— because / — exit ...）。"""
    return ROOT_CAUSE_ZH in full or ROOT_CAUSE_EN in full

def normalize(text: str) -> str:
    """规范化用于查重：去空白、全半角括号、大小写。"""
    t = re.sub(r"\s+", "", text)
    t = t.replace("（", "(").replace("）", ")").replace("：", ":").replace("，", ",")
    return t.lower()

def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [f"{path}: 无法读取（{e}）"]

    rules = []          # (line_no, full_text)
    current = None      # (line_no, 收集中的条目文本)
    seen = {}           # 规范化首句 -> line_no
    warnings = []

    for i, raw in enumerate(text.splitlines(), 1):
        m = RULE_RE.match(raw)
        if m:
            if current:
                rules.append(current)
            current = (i, raw.strip())
            continue
        if current and CONT_RE.match(raw):
            # 续行：累加到当前条目，仅保留含根因标记的文本用于查重
            current = (current[0], current[1] + " " + raw.strip())
            continue
        if current:
            rules.append(current)
            current = None
        # 其他行（标题/注释/表格）跳过
    if current:
        rules.append(current)

    if not rules:
        errors.append(f"{path}: 未找到任何禁则条目（格式应为 `- [领域] 禁止 X —— 因为会 Y`）")
        return errors

    for line_no, full in rules:
        # 1) 根因标记
        if not has_root_cause(full):
            errors.append(f"{path}:{line_no}: 缺少根因标记（中文「—— 因为」或英文 em dash「—」），格式应为 `禁止 X —— 因为会 Y` / `DON'T X — because Y`")
            continue
        # 2) 查重（按根因前的预防性写法部分）
        head = re.split(r"(?:——|—)", full, maxsplit=1)[0]
        key = normalize(head)
        if key in seen:
            errors.append(f"{path}:{line_no}: 疑似重复条目（与第 {seen[key]} 行重复）：{full[:60]}...")
        else:
            seen[key] = line_no

    if len(rules) > MAX_RULES:
        warnings.append(
            f"{path}: 条目数 {len(rules)} 超过 {MAX_RULES}，建议修剪（合并重复/删除过时）"
        )

    for w in warnings:
        print(f"[warn] {w}")
    return errors

def main(argv: list[str]) -> int:
    if not argv:
        print("用法: python scripts/validate_lessons.py <file-or-glob>...", file=sys.stderr)
        return 2
    paths: list[Path] = []
    for arg in argv:
        p = Path(arg)
        if "*" in arg:
            paths.extend(p.parent.glob(p.name))
        elif p.is_file():
            paths.append(p)
    if not paths:
        print("未匹配到任何文件", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for p in sorted(set(paths)):
        all_errors.extend(validate(p))

    if all_errors:
        print("校验失败：")
        for e in all_errors:
            print(f"  [ERROR] {e}")
        return 1
    print(f"[OK] 校验通过（{len(paths)} 个文件）")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
