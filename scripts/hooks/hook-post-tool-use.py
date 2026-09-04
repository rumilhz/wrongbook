#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook-post-tool-use.py —— Reasonix PostToolUse hook（2026-09-04）

工具调用成功后触发：把这次"动手机会"记入事件账本
{"type":"tool_call","toolName":...,"ts":...}，作为生命周期事件窗口的
主数据源（5 家 AI 评审：tool_call 主窗口；PreToolUse 只保留门禁）。

设计：只追加、静默失败、绝不阻塞（见 _ledger.append_event）。
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from _ledger import append_event  # noqa
except Exception:
    def append_event(_ev): return False


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    ev = {
        'type': 'tool_call',
        'ts': datetime.now().isoformat(timespec='seconds'),
        'toolName': str(payload.get('toolName', '?')),
        'cwd': str(payload.get('cwd', '')),
        'mark': 'hook-captured',
    }
    ok = append_event(ev)
    if not ok:
        sys.stderr.write('[hook] ledger append failed (non-blocking)\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())