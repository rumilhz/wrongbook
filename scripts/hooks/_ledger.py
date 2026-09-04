#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_ledger.py —— 共享事件账本写模块（2026-09-04，WrongBook hooks 用）

设计原则（5 家 AI 评审共识）：
- 追加写 O(1)，滚动截断（上限 MAX_ROWS / MAX_BYTES），防无限膨胀
- 写失败 try-catch 静默（绝不让记账拖慢/阻塞 AI 主执行链路）
- shared append：先写后轮转，单行 <8KB 在 Windows 追加语义下基本原子
"""
import json
import os

LEDGER = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'event-ledger.jsonl')
MAX_ROWS = 10000
MAX_BYTES = 5 * 1024 * 1024  # 5MB


def append_event(ev: dict) -> bool:
    """追加一条事件；失败静默返回 False（不抛异常、不影响主流程）。"""
    try:
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        with open(LEDGER, 'a', encoding='utf-8') as f:
            f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        _trim_if_needed()
        return True
    except Exception:
        return False


def _trim_if_needed():
    """滚动截断：超过行数/字节上限时保留尾部 50%（Window 侧批处理，低频）。"""
    try:
        if not os.path.exists(LEDGER):
            return
        if os.path.getsize(LEDGER) <= MAX_BYTES:
            return
        with open(LEDGER, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if len(lines) <= MAX_ROWS:
            return
        keep = lines[-MAX_ROWS:]
        with open(LEDGER, 'w', encoding='utf-8', newline='') as f:
            f.writelines(keep)
    except Exception:
        pass


def count_rows() -> int:
    """行数（audit 用）；异常返回 -1。"""
    try:
        if not os.path.exists(LEDGER):
            return 0
        with open(LEDGER, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)
    except Exception:
        return -1