#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook-post-tool-failure.py —— Reasonix PostToolUseFailure hook（2026-09-02）

工具执行失败时由平台触发：stdin 收到一行 JSON payload，本脚本把事件
追加到 event-ledger.jsonl（Agent 无法伪造的外部事件账本）。
wrongbook-audit.py 将改读此账本（替代 parse 会话猜测），核对率/exposure 变精确。

用法: 由 settings.json hooks.PostToolUseFailure 调用（match=*），
      stdin 读 payload，写 %APPDATA%\\reasonix\\event-ledger.jsonl。
"""
import json
import os
import sys
from datetime import datetime

LEDGER = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'event-ledger.jsonl')


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        payload = {'parse_error': str(e), 'raw': (raw[:200] if 'raw' not in dir() else '')}

    record = {
        'ts': datetime.now().isoformat(timespec='seconds'),
        'event': payload.get('event', 'PostToolUseFailure'),
        'toolName': payload.get('toolName', '?'),
        'cwd': payload.get('cwd', ''),
        'exit_info': str(payload.get('toolResult', ''))[:300],
        'mark': 'hook-captured',
    }
    try:
        with open(LEDGER, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print('[hook] failure captured ->', LEDGER)
    except Exception as e:
        print('[hook] ledger write failed:', e)
    return 0


if __name__ == '__main__':
    sys.exit(main())