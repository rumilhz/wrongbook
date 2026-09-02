#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""add-lesson.py —— WrongBook 一键沉淀脚手架（2026-09-02）

用法:
    python add-lesson.py "<规则文本>" [--kind new|extend]

规则文本 = 一条完整禁则，如:
    "[bash] 禁止直接 ls 可能不存在的路径 —— 因为 exit 2 会让命令判 failed；先 [ -d p ] &&"

自动完成:
  1. 追加/合并到权威全文 %APPDATA%\\reasonix\\self-improvement-lessons.md
  2. 在仓库 data/validation-log.md 追加 RULE 行（[today] RULE 新增/扩充 条目=「...」）
  3. 同步配置包副本（reasonix-config-pack/config/）
  4. 基本格式自检（领域标签 + 因果分隔）
退出码: 0=成功 1=失败
"""
import os
import re
import sys
from datetime import date

APPROOT = os.path.join(os.environ.get('APPDATA', ''), 'reasonix')
LESSONS = os.path.join(APPROOT, 'self-improvement-lessons.md')

# 从本脚本位置推断仓库根：<repo>/scripts/add-lesson.py
_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo():
    # 1) 脚本位于 <repo>/scripts/ 下
    if os.path.basename(_HERE) == 'scripts':
        return os.path.abspath(os.path.join(_HERE, '..'))
    # 2) 环境变量显式指定
    ev = os.environ.get('WRONGBOOK_REPO')
    if ev and os.path.isdir(ev):
        return ev
    # 3) 常见路径（全局副本也能定位仓库）
    for cand in (
        r'D:\Workplace\配置\preflight-lessons',
        os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'preflight-lessons'),
    ):
        if os.path.isdir(cand):
            return cand
    return None


_REPO = _find_repo()
LOG = os.path.join(_REPO, 'data', 'validation-log.md') if _REPO else None
# 配置包副本：repo 同级 ../reasonix-config-pack/config/ 或 .../配置/reasonix-config-pack/config/
_PACK = None
if _REPO:
    for cand in (
        os.path.abspath(os.path.join(_REPO, '..', 'reasonix-config-pack', 'config', 'self-improvement-lessons.md')),
        os.path.abspath(os.path.join(_REPO, '..', 'config', 'self-improvement-lessons.md')),
    ):
        if os.path.exists(os.path.dirname(cand)):
            _PACK = cand
            break


def fail(msg: str) -> int:
    print('[ERROR]', msg)
    return 1


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not argv:
        print('usage: python add-lesson.py "<rule>" [--kind new|extend]')
        return 1
    rule = argv[0].strip()
    kind = 'extend' if '--kind' in sys.argv and 'extend' in sys.argv else 'new'

    # 1) 基本格式自检
    if not re.search(r'\[[^]]+\]', rule.split(' ')[0] if rule.startswith('- ') else rule):
        # 无领域标签
        pass
    if not re.search(r'(禁止|DON\'T|不要|避免|勿|别)', rule):
        return fail('rule does not look like a prohibition (no 禁止/DON\'T): ' + rule[:60])
    if '——' not in rule and '--' not in rule:
        return fail('rule lacks reason separator (——): ' + rule[:60])
    if not rule.startswith('- ['):
        rule = '- ' + rule

    # 2) 权威全文（%APPDATA%，全局副本；无则建）
    if not os.path.exists(LESSONS):
        with open(LESSONS, 'w', encoding='utf-8', newline='') as f:
            f.write('# self-improvement-lessons.md - authoritative lessons\n\n')
    with open(LESSONS, 'r', encoding='utf-8') as f:
        content = f.read()

    head = rule[:24]  # 用于查重的前缀
    dup = [ln for ln in content.split('\n') if ln.strip().startswith('- [') and head in ln]
    if dup and kind == 'new':
        print('[SKIP] duplicate-ish exists, use --kind extend or edit that entry manually:')
        print('   ', dup[0][:90])
        return 1

    with open(LESSONS, 'a', encoding='utf-8', newline='') as f:
        f.write('\n' + rule if not content.endswith('\n') else rule + '\n')
    print('[OK] appended to lessons file:', os.path.basename(LESSONS))

    # 3) validation-log（若脚本在仓库内）
    if LOG and os.path.exists(os.path.dirname(LOG)):
        today = date.today().isoformat()
        kind_label = {'new': '新增', 'extend': '扩充'}.get(kind, kind)
        entry = '- [{}] RULE {} 条目=「{}」\n'.format(today, kind_label, rule[2:])
        with open(LOG, 'a', encoding='utf-8', newline='') as f:
            f.write(entry)
        print('[OK] RULE logged ->', os.path.relpath(LOG))
    else:
        print('[SKIP] validation-log not found (global copy); log manually')

    # 4) 配置包副本同步
    if _PACK and os.path.exists(os.path.dirname(_PACK)):
        with open(_PACK, 'w', encoding='utf-8', newline='') as f:
            f.write(open(LESSONS, 'r', encoding='utf-8').read())
        print('[OK] config-pack synced ->', os.path.basename(os.path.dirname(_PACK)))

    return 0


if __name__ == '__main__':
    sys.exit(main())
