#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate-rule-index.py —— 从错题本全文按领域生成切片索引（2026-09-02）

用途: 规则切片化 + 触发式检索的导航层。将全文 76 条禁则按主域聚合，
生成 rule-index.md：「主域 → 规则清单（标题级）」，Agent 核对时按
动作→领域 只读相关领域的规则标题，命中后再回全文取原文。

用法:
  python generate-rule-index.py [--out <path>]   # 默认写 <全文同目录>/rule-index.md

维护: 主域映射表 domain_map 随新领域沉淀更新。
"""
import os
import re
import sys

DOMAIN_MAP = [
    # (主域, 匹配子域关键词列表, 动作类型→查它)
    ('bash', ['bash'], '执行 shell/命令'),
    ('PowerShell/Windows', ['PowerShell', 'Windows/PS', 'PS'], '执行 shell/命令'),
    ('脚本/编码/Python', ['脚本', 'Python', '编码', '解压'], '写代码/改文件'),
    ('Reasonix/平台', ['Reasonix'], '调工具/平台'),
    ('工具/配额/API', ['工具', '配额', '搜索配额', 'MCP', 'Ollama'], '调工具/API/MCP'),
    ('安装/部署', ['安装', 'skill'], '装包/改配置'),
    ('WSL/网络/挂载', ['WSL', '网络', 'WebDAV', '坚果云', 'Ollama/代理'], '路径/跨系统传文件'),
    ('浏览器/CDP', ['CDP', 'BrowserAct', '浏览器'], '调工具/浏览器'),
    ('多媒体/ffmpeg', ['ffmpeg'], '写代码/多媒体'),
    ('评测/调度/续跑', ['评测', '调度', '增量续跑', 'CER'], '评测/批处理'),
    ('宿主/后台/守护', ['宿主', '后台'], '执行 shell/命令'),
    ('文件/存储', ['文件', 'Windows/文件', 'Windows/subprocess'], '路径/跨系统传文件'),
    ('GUI/桌面', ['GUI', 'tkinter'], '写代码/GUI'),
    ('Zotero/文献', ['Zotero'], '调工具/Zotero'),
    ('Jellyfin/Emby', ['Jellyfin', 'Emby'], '调工具/媒体服务'),
]

CORE_HEADER = '## 核心禁则'
APP_HEADER = '## 参考禁则'


def domain_of(rule_line: str) -> str:
    m = re.match(r'^\s*-\s*\[([^\]]+)\]', rule_line)
    if not m:
        return '未分类'
    tag = m.group(1)
    for main, keys, _ in DOMAIN_MAP:
        if any(k in tag for k in keys):
            return main
    return tag


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(here, '..')) if os.path.basename(here) == 'scripts' else here
    # 全文位置：优先仓库外 %APPDATA%，回退仓库内
    ext = os.path.join(os.environ.get('APPDATA', ''), 'reasonix', 'self-improvement-lessons.md')
    if not os.path.exists(ext):
        ext = os.path.join(repo, 'lessons.md')
    if not os.path.exists(ext):
        print('[ERROR] lessons file not found')
        return 1

    with open(ext, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    core = []
    appendix = []
    section = None
    for ln in lines:
        s = ln.strip()
        if CORE_HEADER in s:
            section = 'core'
            continue
        if APP_HEADER in s:
            section = 'appendix'
            continue
        if s.startswith('- ['):
            if section == 'core':
                core.append(ln)
            else:
                appendix.append(ln)

    def build(entries):
        groups = {}
        for e in entries:
            dom = domain_of(e)
            title = re.sub(r'^\s*-\s*\[[^\]]+\]\s*', '', e).strip()
            title = title.split('——')[0][:48]
            groups.setdefault(dom, []).append(title)
        return groups

    core_g, app_g = build(core), build(appendix)

    out = []
    out.append('# rule-index.md —— 错题本领域切片索引（自动生成，勿手改）')
    out.append('')
    out.append('> 由 scripts/generate-rule-index.py 从权威全文生成。核对流程：')
    out.append('> 1) 动作类型 → 主域（见 REASONIX.md 映射表）')
    out.append('> 2) 在本索引查该主域规则标题（命中候选）')
    out.append('> 3) 回权威全文读原文 → 判定命中/无命中 → 写 [错题本核对] 行')
    out.append('')
    out.append('## 核心域（常驻 12 条）')
    out.append('')
    for dom in sorted(core_g):
        out.append('### %s' % dom)
        for t in core_g[dom]:
            out.append('- %s' % t)
        out.append('')
    out.append('## 参考域（按需检索 64 条）')
    out.append('')
    for dom in sorted(app_g):
        out.append('### %s' % dom)
        for t in app_g[dom]:
            out.append('- %s' % t)
        out.append('')

    index_path = os.path.join(os.path.dirname(ext), 'rule-index.md')
    with open(index_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(out) + '\n')

    print('[OK] rule-index.md generated:', index_path)
    print('     core entries:', len(core), ' appendix:', len(appendix))
    return 0


if __name__ == '__main__':
    sys.exit(main())