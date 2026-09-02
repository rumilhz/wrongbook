#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wrongbook-audit.py —— 会话日志外部审计 + 规则生命周期打分（v2，2026-09-02）

用途: 对抗 self-reporting 的最小外部审计（不拦 Agent、只读日志）。
v1 提供聚合对账：核对率 / 命中率 / exposure top。
v2 新增规则生命周期（docs/validation.md §1.6）：
  - 按规则统计 exposure / hit（从规则库关键词匹配核对行）
  - 计算 RiskScore = 命中率×0.5 + 暴露归一化×0.3 + 影响×0.2
  - 输出 promotion / demotion / expiry 三清单（人工确认后执行）

用法:
  python wrongbook-audit.py <jsonl|dir> [--rules <lessons.md>] [--top N] [--window N]
  --rules 缺省时自动找 %APPDATA%\\reasonix\\self-improvement-lessons.md
  --window N 事件窗口=最近 N 个活跃会话（默认 20；窗口内统计，防闲置期误判淘汰）
"""
import os
import re
import sys
from collections import Counter

CHECK_RE = re.compile(r'\[错题本核对\]')
HIT_RE = re.compile(r'\[错题本核对\].*?(命中|改用|→|->)')
TOOL_RE = re.compile(r'"name"\s*:\s*"(bash|run_skill|edit_file|write_file|read_file|web_fetch)"', re.I)

CORE_HDR, APP_HDR = '## 核心禁则', '## 参考禁则'


def load_rules(lessons_path: str):
    """解析规则库，返回 [(section, domain, title, keywords)]"""
    rules = []
    with open(lessons_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.read().split('\n')
    section = None
    for ln in lines:
        s = ln.strip()
        if CORE_HDR in s:
            section = 'core'
            continue
        if APP_HDR in s:
            section = 'appendix'
            continue
        m = re.match(r'^- \[([^\]]+)\]\s*(.+)$', s)
        if m and section:
            dom, title = m.group(1), m.group(2)
            title = title.split('——')[0].strip()
            # 关键词 = 标题前 6 字（域标签太宽泛会虚高 exposure，只用作回退）
            keywords = [title[:6]] if len(title) >= 4 else [title]
            rules.append({'section': section, 'domain': dom, 'title': title[:30],
                          'keywords': keywords})
    return rules


def scan_file(path: str, rules) -> tuple:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    checks = len(CHECK_RE.findall(text))
    hits = len(HIT_RE.findall(text))
    tools = len(TOOL_RE.findall(text))
    exp = Counter()
    hcnt = Counter()
    for m in re.finditer(r'\[错题本核对\][^\n]{0,150}', text):
        seg = m.group(0)
        is_hit = bool(re.search(r'命中|改用|→|->', seg))
        for r in rules:
            if any(k and k in seg for k in r['keywords']):
                exp[r['title']] += 1
                if is_hit:
                    hcnt[r['title']] += 1
    return {'checks': checks, 'hits': hits, 'tools': tools, 'exp': exp, 'hcnt': hcnt}


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print('usage: python wrongbook-audit.py <jsonl|dir> [--rules <lessons.md>] [--top N]')
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
    window = 20  # 事件窗口：最近 N 个活跃会话（docs/validation.md §1.6 v0.3）
    if '--window' in argv:
        try:
            window = int(argv[argv.index('--window') + 1])
        except (ValueError, IndexError):
            pass

    # 规则库
    lessons = None
    if '--rules' in argv:
        lessons = argv[argv.index('--rules') + 1]
    else:
        cand = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'self-improvement-lessons.md')
        if os.path.exists(cand):
            lessons = cand
    rules = load_rules(lessons) if lessons else []

    files = []
    if os.path.isdir(target):
        for root, _, names in os.walk(target):
            for n in names:
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

    # 事件窗口：按 mtime 排序，最近 window 个会话为主窗口；超期文件为历史（不影响窗口判定）
    files.sort(key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0, reverse=True)
    window_files = files[:window]

    totals = {'checks': 0, 'hits': 0, 'tools': 0}
    exp_all, hcnt_all = Counter(), Counter()
    win_exp, win_hcnt = Counter(), Counter()
    for f in sorted(files):
        r = scan_file(f, rules)
        for k in ('checks', 'hits', 'tools'):
            totals[k] += r[k]
        exp_all.update(r['exp'])
        hcnt_all.update(r['hcnt'])
        if f in window_files:
            win_exp.update(r['exp'])
            win_hcnt.update(r['hcnt'])

    X, Y, H = totals['tools'], totals['checks'], totals['hits']
    print('=== wrongbook-audit v2 report (event-window) ===')
    print('files scanned        :', len(files))
    print('event window         : latest %d active sessions (%d files total)' % (min(window, len(files)), len(files)))
    print('tool calls X         :', X)
    print('preflight checks Y   :', Y)
    print('hit lines H          :', H)
    if X:
        print('compliance Y/X       : {:.1%}'.format(Y / X))
    if Y:
        print('hit rate H/Y         : {:.1%}'.format(H / Y))

    if rules:
        print('rules loaded         :', len(rules), '(core+ref)')
        # 每条规则打分 —— 用窗口统计（win_exp/win_hcnt），防闲置期误判
        rows = []
        for r in rules:
            e = win_exp.get(r['title'], 0)
            h = win_hcnt.get(r['title'], 0)
            impact = 3 if r['section'] == 'core' else 1
            hit_rate = (h / e) if e else 0.0
            score = hit_rate * 0.5 + min(e / 50.0, 1.0) * 0.3 + impact * 0.2 / 3.0
            rows.append({**r, 'exp': e, 'hit': h, 'hit_rate': hit_rate, 'score': score})
        rows.sort(key=lambda x: -x['score'])
        print('--- rule lifecycle scoring (top %d by RiskScore, window) ---' % min(top, len(rows)))
        for r in rows[:top]:
            print('  [%s] %-8s e=%-4d h=%-3d rate=%-5.0f%% score=%.2f  %s'
                  % (r['section'], r['domain'][:8], r['exp'], r['hit'],
                     r['hit_rate'] * 100, r['score'], r['title']))
        # 三清单（阈值对齐 docs/validation.md §1.6；窗口内判定防闲置误伤）
        promo = [r for r in rows if r['section'] == 'appendix'
                 and (r['exp'] >= 15 and r['hit_rate'] >= 0.3)]
        demo = [r for r in rows if r['section'] == 'core'
                and (r['exp'] < 5 or (r['hit_rate'] < 0.1 and r['hit'] == 0))]
        expiry = [r for r in rows if r['exp'] == 0 and r['hit'] == 0]
        print('--- lifecycle candidates (manual confirm, window-based) ---')
        print('  PROPOSED CORE: %d' % len(promo))
        for r in promo[:5]:
            print('    + %s (e=%d rate=%.0f%%)' % (r['title'], r['exp'], r['hit_rate'] * 100))
        print('  PROPOSED DEMOTE: %d' % len(demo))
        for r in demo[:5]:
            print('    - %s (e=%d)' % (r['title'], r['exp']))
        print('  EXPIRY CANDIDATES: %d (window e=0,h=0; 需连续2窗口才淘汰)' % len(expiry))
        for r in expiry[:5]:
            print('    x %s' % r['title'])
    else:
        print('[WARN] no rules loaded — pass --rules <lessons.md> for lifecycle scoring')

    if X and Y < X * 0.2:
        print('[INVALID] 操作数/核对数 > 5:1 — 本次数据不参与升降级（docs/validation.md §1.6 数据失效保护）')
    elif Y < X * 0.8:
        print('[WARN] compliance < 80% — 核对仪式未持续执行')
    return 0


if __name__ == '__main__':
    sys.exit(main())