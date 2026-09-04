#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook-session-start.py —— Reasonix SessionStart hook（2026-09-02，v2 压缩摘要版）

把错题本「核心禁则」压缩为**一行触发词摘要**注入会话（≤1500 字符），
避免长句堆砌造成的注意力噪音（5 家 AI 评审共识：SessionStart 只做弱提醒）。
真正的强制交给 hook-pre-tool-use.py（PreToolUse 门禁）。
"""
import os
import re
import sys

LESSONS = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'self-improvement-lessons.md')


def compact(line: str) -> str:
    """把一条禁则压成「领域|触发场景」触发词。"""
    m = re.match(r'^\s*-\s*\[([^\]]+)\]\s*禁止(.+?)(?:——|；|$)', line)
    if m:
        dom = m.group(1)
        what = m.group(2).strip()
        # 取禁止的对象短语（去写法/去根因细节）
        if '——' in what:
            what = what.split('——')[0]
        what = re.sub(r'（.*?）', '', what)[:26]
        return '[%s] 禁%s' % (dom[:14], what)
    return line[:40]


def extract_core(text: str):
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
            core.append(compact(s))
    return core


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    if not os.path.exists(LESSONS):
        print('【错题本】核心规则文件缺失，本会话跳过自动注入。')
        return 0
    with open(LESSONS, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    core = extract_core(text)
    if not core:
        return 0
    body = '【错题本·核心禁则（触发词速查，动手前核对；高危已由 PreToolUse 硬拦截）】\n' + '\n'.join(core)
    if len(body) > 1500:
        body = body[:1500] + '\n…(截断)'
    print(body)
    return 0


if __name__ == '__main__':
    sys.exit(main())