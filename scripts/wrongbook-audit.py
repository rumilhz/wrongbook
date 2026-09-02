#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wrongbook-audit.py —— 扫会话日志做聚合对账（2026-09-02）

用途: 对抗 self-reporting 的最小外部审计。不拦 Agent、只读日志，计算:
  - 工具调用次数 X（bash 工具 call 计数）
  - PREFLIGHT 核对行次数 Y（[错题本核对] 出现次数, 统一计 agent 输出的核对行）
  - 核对率 Compliance = Y / X
  - 命中行次数 H（核对行含「命中/改用/→」字样）
  - exposure 粗计数（命中行里引用的规则条目名 top N）

用法:
  python wrongbook-audit.py <会话jsonl路径或目录> [--top 10]

说明:
  - 会话文件为 Reasonix 的 events/transcript jsonl（含 assistant 消息文本）。
  - 只做 grep 级统计，不解析结构，够用且零依赖。
"""
import os
import re
import sys
from collections import Counter

CHECK_RE = re.compile(r'\[错题本核对\]')
HIT_RE = re.compile(r'\[错题本核对\].*?(命中|改用|→|->)')
TOOL_RE = re.compile(r'"name"\s*:\s*"(bash|run_skill|edit_file|write_file|read_file|web_fetch)"', re.I)


def scan_file(path: str) -> dict:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    checks = CHECK_RE.findall(text)
    hits = HIT_RE.findall(text)
    tools = TOOL_RE.findall(text)
    # exposure 粗提取：命中行内「条目名」候选（「」间或 命中X 后的短语）
    exposures = Counter()
    for m in re.finditer(r'\[错题本核对\][^\n]{0,120}', text):
        seg = m.group(0)
        for name in re.findall(r'「([^」]{2,20})」', seg):
            exposures[name] += 1
        m2 = re.search(r'(?:命中|改用)\s*([^，。；\s、→>]{2,16})', seg)
        if m2:
            exposures[m2.group(1).strip()[:14]] += 1
    return {'checks': len(checks), 'hits': len(hits), 'tools': len(tools), 'exposures': exposures}


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print('usage: python wrongbook-audit.py <jsonl|dir> [--top N]')
        return 1
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    target = argv[0]
    top = 10
    if '--top' in argv:
        try:
            top = int(argv[argv.index('--top') + 1])
        except (ValueError, IndexError):
            pass

    files = []
    if os.path.isdir(target):
        for root, _, names in os.walk(target):
            for n in names:
                # 只扫主转录 <会话名>.jsonl：排除派生文件（events/event-index/display-index/meta）
                if n.endswith('.jsonl') and not any(
                    k in n for k in ('events.jsonl', 'event-index', 'display-index', '.meta')
                ):
                    files.append(os.path.join(root, n))
    elif os.path.isfile(target):
        files = [target]
    else:
        print('[ERROR] target not found:', target)
        return 1

    if not files:
        print('[ERROR] no .jsonl found under', target)
        return 1

    total = {'checks': 0, 'hits': 0, 'tools': 0}
    exp = Counter()
    for f in sorted(files):
        r = scan_file(f)
        for k in ('checks', 'hits', 'tools'):
            total[k] += r[k]
        exp.update(r['exposures'])

    X, Y, H = total['tools'], total['checks'], total['hits']
    print('=== wrongbook-audit report ===')
    print('files scanned        :', len(files))
    print('tool calls X         :', X)
    print('preflight checks Y   :', Y)
    print('hit lines H          :', H)
    if X > 0:
        print('compliance Y/X       : {:.1%}'.format(Y / X))
    if Y > 0:
        print('hit rate H/Y         : {:.1%}'.format(H / Y))
    print('--- exposure top %d ---' % top)
    for name, n in exp.most_common(top):
        print('  %-18s %d' % (name, n))
    if Y < X * 0.8:
        print('[WARN] compliance < 80% — 核对仪式未持续执行，见 docs/validation.md §1.5')
    return 0


if __name__ == '__main__':
    sys.exit(main())