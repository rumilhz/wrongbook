#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook-pre-tool-use.py —— Reasonix PreToolUse 高危门禁（2026-09-02，5 家 AI 评审共识）

只对**破坏性/不可逆**的高危命令做 exit 2 真阻断（正则匹配，不依赖 LLM 判断），
其余一律放行。白名单路径可绕行（干预脚本自身或容器内安全删除等合法场景）。

协议: stdin 收一行 JSON payload（event/cwd/toolName/toolArgs…）
  - 命中高危规则且非白名单 → 输出拒绝理由到 stderr、exit 2（平台阻断该工具调用）
  - 未命中/白名单 → exit 0（放行）
超时兜底: 调用方（settings.json）设短 timeout，超时平台按"不阻塞"放行。
"""
import json
import os
import re
import sys

# 高危规则：破坏性 / 强制覆盖 / 权限变更 / 管道执行外部脚本
HIGH_RISK = [
    (re.compile(r'(^|\s|;|\|)(rm|rmdir|del|rd)\s+(-[rf]+\s+)?(/\s*|/[\w.-]+|~|\.\.[\\/])', re.I),
     '高危删除（rm -rf 等）'),
    (re.compile(r'git\s+push\s+.*(--force| -f\b)', re.I), '强制推送（git push --force）'),
    (re.compile(r'(chmod\s+777|chown\s+0:0)\s+/', re.I), '权限/属主变更到根'),
    (re.compile(r'\bcurl\b.*\|\s*(ba)?sh\b', re.I), '管道执行外部脚本（curl|sh）'),
    (re.compile(r'(pip|pip3)\s+install\b.*(--no-verify)', re.I), 'pip 免验证安装'),
    (re.compile(r'(mkfs|format|fdisk|dd)\s+of=', re.I), '磁盘级破坏（mkfs/dd）'),
]
# 白名单：这些路径/场景下的操作放行（干预流程、容器内、任务临时目录）
WHITELIST_DIRS = (
    os.path.dirname(os.path.abspath(__file__)),          # hooks 脚本所在目录
    r'/tmp', r'/var/tmp',                                # 临时目录
)
SSH_CAVEAT = ('bash',)  # 高危判定只在 bash/shell 类工具执行


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    tool = str(payload.get('toolName', ''))
    args = str(payload.get('toolArgs', ''))
    cwd = str(payload.get('cwd', ''))
    if tool not in SSH_CAVEAT and tool != '':
        return 0  # 非 shell 工具不拦
    # 白名单：仅按 cwd 判定（脚本自身目录/安全临时根）；不按 args 子串（避免 rm -rf /tmp 被误放行）
    if any(cwd.startswith(wd) for wd in WHITELIST_DIRS):
        return 0
    for rx, label in HIGH_RISK:
        if rx.search(args):
            reason = 'wrongbook 高危门禁: %s（如需执行请走白名单路径或人工确认）' % label
            sys.stderr.write(reason + '\n')
            return 2  # 平台语义：exit 2 = 阻断该工具调用
    return 0


if __name__ == '__main__':
    sys.exit(main())