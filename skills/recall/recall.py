# -*- coding: utf-8 -*-
"""
Memory Recall - 混合检索脚本
供 recall Skill 调用，执行向量 70% + BM25 30% 混合检索

用法:
    python -X utf8 recall.py "登录模块 优化"
    python -X utf8 recall.py "部署" --table instincts
    python -X utf8 recall.py "bug修复" --limit 10
"""

import sys
import json
import argparse
from pathlib import Path

# 添加 hooks 目录到 path
hooks_dir = Path.home() / ".claude" / "hooks"
sys.path.insert(0, str(hooks_dir))

from memory_store import MemoryStore
from config import RECALL_MAX_RESULTS, INSTINCT_MATURE_THRESHOLD, INSTINCT_MIN_EVIDENCE


def format_observation(obs: dict) -> str:
    """格式化单条 observation"""
    content = obs.get('content', '')
    tags = obs.get('tags', '[]')
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = []
    created = obs.get('created_at', '')[:10]
    obs_type = obs.get('type', '')
    project = obs.get('project', '')

    parts = []
    if created:
        parts.append(f"[{created}]")
    if project:
        parts.append(f"({project})")
    if obs_type:
        parts.append(f"<{obs_type}>")
    parts.append(content)
    if tags:
        parts.append(f"  tags: {', '.join(tags)}")
    return ' '.join(parts)


def format_instinct(inst: dict) -> str:
    """格式化单条 instinct"""
    confidence = inst.get('confidence', 0)
    trigger = inst.get('trigger', '')
    action = inst.get('action', '')
    domain = inst.get('domain', '')
    evidence = inst.get('evidence', '[]')
    if isinstance(evidence, str):
        try:
            evidence = json.loads(evidence)
        except Exception:
            evidence = []

    bar_len = int(confidence * 10)
    bar = '█' * bar_len + '░' * (10 - bar_len)
    mature = ' ★MATURE' if confidence >= INSTINCT_MATURE_THRESHOLD and len(evidence) >= INSTINCT_MIN_EVIDENCE else ''

    return (
        f"  {bar} {confidence:.0%}{mature}\n"
        f"    trigger: {trigger}\n"
        f"    action: {action}\n"
        f"    domain: {domain}, evidence: {len(evidence)}"
    )


def main():
    parser = argparse.ArgumentParser(description='Memory Recall - 混合检索')
    parser.add_argument('query', type=str, help='检索关键词')
    parser.add_argument('--table', type=str, default='both', choices=['observations', 'instincts', 'both'],
                        help='检索哪个表')
    parser.add_argument('--limit', type=int, default=None, help='返回条数')
    args = parser.parse_args()

    store = MemoryStore()
    limit = args.limit or RECALL_MAX_RESULTS

    output_parts = []

    # 检索 observations
    if args.table in ('observations', 'both'):
        obs_results = store.hybrid_search(args.query, source_table='observations', limit=limit)
        if obs_results:
            output_parts.append(f"## Observations ({len(obs_results)} 条)")
            for obs in obs_results:
                output_parts.append(format_observation(obs))
        else:
            output_parts.append("## Observations: 无匹配结果")

    # 检索 instincts
    if args.table in ('instincts', 'both'):
        inst_results = store.hybrid_search(args.query, source_table='instincts', limit=min(limit, 10))
        if inst_results:
            output_parts.append(f"\n## Instincts ({len(inst_results)} 条)")
            for inst in inst_results:
                output_parts.append(format_instinct(inst))
        else:
            output_parts.append("\n## Instincts: 无匹配结果")

    # 检查成熟直觉
    mature = store.get_mature_instincts()
    if mature:
        output_parts.append(f"\n## 成熟直觉 ({len(mature)} 条，建议 self-evolve)")
        for inst in mature:
            output_parts.append(format_instinct(inst))

    print('\n'.join(output_parts))


if __name__ == '__main__':
    main()
