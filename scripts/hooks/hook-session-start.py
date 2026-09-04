#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook-session-start.py —— Reasonix SessionStart hook（2026-09-02）

把错题本「核心禁则」摘要输出到 stdout，Reasonix 自动注入为
本会话 <hook-context>（一次性上下文），实现强制前置注入：
Agent 每轮开场即见规则，核对从"自觉"变"必然"。

输出规范：stdout 纯文本（≤ ~8000 字符），stderr 留空（避免污染）。
"""
import os
import sys

LESSONS = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'self-improvement-lessons.md')


def extract_core(text: str) -> str:
    """取「核心禁则」区到「参考禁则」区之间的规则，压缩为一行摘要。"""
    lines = text.split('\n')
    in_core = False
    core = []
    for ln in lines:
        s = ln.strip()
        if '核心禁则' in s:
            in_core = True
            continue
        if '参考禁则' in s:
            break
        if in_core and s.startswith('- ['):
            core.append(s)
    return '\n'.join(core)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    if not os.path.exists(LESSONS):
        print('''【错题本】核心规则文件缺失，本会话跳过自动注入。''')
        return 0
    with open(LESSONS, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    core = extract_core(text)
    if not core:
        return 0
    header = '【错题本·核心禁则（自动注入，动手前核对，命中即换写法）】'
    body = header + '\n' + core + '\n【以上为本会话前置核对清单】'
    if len(body) > 9000:
        body = body[:9000] + '\n…(截断)'
    print(body)
    return 0


if __name__ == '__main__':
    sys.exit(main())