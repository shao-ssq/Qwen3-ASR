"""生成 GRAPH_REPORT.md — 人类可读的图谱审计 trail。

核心职责: 将图、社区、分析结果组装为结构化的 Markdown 报告，包含语料库检查、
         摘要、社区结构、上帝节点、意外连接、超边、知识缺口、建议问题。

公共方法:
    generate(G, communities, cohesion, labels, god_nodes, surprises,
             detection, tokens, root, suggested_questions) - 生成报告 Markdown 字符串

报告结构 (按顺序):
    1) Corpus Check      - 语料库规模检查 + 是否需要图谱的判定
    2) Summary           - 节点/边/社区数 + 边置信度分布 + Token 消耗
    3) Community Hubs    - 社区导航链接 (指向 Obsidian vault 的 _COMMUNITY_*.md)
    4) God Nodes         - 连接度最高的核心实体
    5) Surprising Connections - 意外跨文件/跨社区连接 (含置信度分数和原因)
    6) Hyperedges        - 超边 (3+ 节点的组关系)
    7) Communities       - 每个社区的名称、内聚度、成员节点 (过滤方法存根)
    8) Ambiguous Edges   - AMBIGUOUS 置信度的边，需人工审查
    9) Knowledge Gaps    - 孤立节点 + 薄社区 + 高比例 AMBIGUOUS
    10) Suggested Questions - 基于图结构生成的建议问题

内部辅助方法:
    _safe_community_name() - 清理社区标签中的非法字符，确保 Obsidian 文件名合法

关键设计:
    - 上帝节点和方法存根 (_is_file_node) 从社区展示中过滤
    - 社区导航链接 (_COMMUNITY_*.md) 防止 vault 分裂为不连通组件
    - 置信度统计: EXTRACTED / INFERRED / AMBIGUOUS 百分比 + INFERRED 平均分数
    - 知识缺口: 孤立节点 (≤1 边) + 薄社区 (<3 节点) + 高 AMBIGUOUS 比例 (>20%)
"""
from __future__ import annotations
import re
from datetime import date
import networkx as nx


def _safe_community_name(label: str) -> str:
    """Mirrors export.safe_name so community hub filenames and report wikilinks always agree."""
    cleaned = re.sub(r'[\\/*?:"<>|#^[\]]', "", label.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")).strip()
    cleaned = re.sub(r"\.(md|mdx|markdown)$", "", cleaned, flags=re.IGNORECASE)
    return cleaned or "unnamed"


def generate(
    G: nx.Graph,
    communities: dict[int, list[str]],
    cohesion_scores: dict[int, float],
    community_labels: dict[int, str],
    god_node_list: list[dict],
    surprise_list: list[dict],
    detection_result: dict,
    token_cost: dict,
    root: str,
    suggested_questions: list[dict] | None = None,
) -> str:
    today = date.today().isoformat()

    confidences = [d.get("confidence", "EXTRACTED") for _, _, d in G.edges(data=True)]
    total = len(confidences) or 1
    ext_pct = round(confidences.count("EXTRACTED") / total * 100)
    inf_pct = round(confidences.count("INFERRED") / total * 100)
    amb_pct = round(confidences.count("AMBIGUOUS") / total * 100)

    inf_edges = [(u, v, d) for u, v, d in G.edges(data=True) if d.get("confidence") == "INFERRED"]
    inf_scores = [d.get("confidence_score", 0.5) for _, _, d in inf_edges]
    inf_avg = round(sum(inf_scores) / len(inf_scores), 2) if inf_scores else None

    lines = [
        f"# Graph Report - {root}  ({today})",
        "",
        "## Corpus Check",
    ]
    if detection_result.get("warning"):
        lines.append(f"- {detection_result['warning']}")
    else:
        lines += [
            f"- {detection_result['total_files']} files · ~{detection_result['total_words']:,} words",
            "- Verdict: corpus is large enough that graph structure adds value.",
        ]

    lines += [
        "",
        "## Summary",
        f"- {G.number_of_nodes()} nodes · {G.number_of_edges()} edges · {len(communities)} communities detected",
        f"- Extraction: {ext_pct}% EXTRACTED · {inf_pct}% INFERRED · {amb_pct}% AMBIGUOUS"
        + (f" · INFERRED: {len(inf_edges)} edges (avg confidence: {inf_avg})" if inf_avg is not None else ""),
        f"- Token cost: {token_cost.get('input', 0):,} input · {token_cost.get('output', 0):,} output",
    ]

    # Community hub navigation - links to _COMMUNITY_*.md files in the Obsidian vault.
    # Without these, GRAPH_REPORT.md is a dead-end and the vault splits into disconnected components.
    if communities:
        lines += ["", "## Community Hubs (Navigation)"]
        for cid in communities:
            label = community_labels.get(cid, f"Community {cid}")
            safe = _safe_community_name(label)
            lines.append(f"- [[_COMMUNITY_{safe}|{label}]]")

    lines += [
        "",
        "## God Nodes (most connected - your core abstractions)",
    ]
    for i, node in enumerate(god_node_list, 1):
        lines.append(f"{i}. `{node['label']}` - {node['edges']} edges")

    lines += ["", "## Surprising Connections (you probably didn't know these)"]
    if surprise_list:
        for s in surprise_list:
            relation = s.get("relation", "related_to")
            note = s.get("note", "")
            files = s.get("source_files", ["", ""])
            conf = s.get("confidence", "EXTRACTED")
            cscore = s.get("confidence_score")
            if conf == "INFERRED" and cscore is not None:
                conf_tag = f"INFERRED {cscore:.2f}"
            else:
                conf_tag = conf
            sem_tag = " [semantically similar]" if relation == "semantically_similar_to" else ""
            lines += [
                f"- `{s['source']}` --{relation}--> `{s['target']}`  [{conf_tag}]{sem_tag}",
                f"  {files[0]} → {files[1]}" + (f"  _{note}_" if note else ""),
            ]
    else:
        lines.append("- None detected - all connections are within the same source files.")

    hyperedges = G.graph.get("hyperedges", [])
    if hyperedges:
        lines += ["", "## Hyperedges (group relationships)"]
        for h in hyperedges:
            node_labels = ", ".join(h.get("nodes", []))
            conf = h.get("confidence", "INFERRED")
            cscore = h.get("confidence_score")
            conf_tag = f"{conf} {cscore:.2f}" if cscore is not None else conf
            lines.append(f"- **{h.get('label', h.get('id', ''))}** — {node_labels} [{conf_tag}]")

    lines += ["", "## Communities"]
    from .analyze import _is_file_node as _ifn
    for cid, nodes in communities.items():
        label = community_labels.get(cid, f"Community {cid}")
        score = cohesion_scores.get(cid, 0.0)
        # Filter method/function stubs from display - they're structural noise
        real_nodes = [n for n in nodes if not _ifn(G, n)]
        display = [G.nodes[n].get("label", n) for n in real_nodes[:8]]
        suffix = f" (+{len(real_nodes)-8} more)" if len(real_nodes) > 8 else ""
        lines += [
            "",
            f"### Community {cid} - \"{label}\"",
            f"Cohesion: {score}",
            f"Nodes ({len(real_nodes)}): {', '.join(display)}{suffix}",
        ]

    ambiguous = [(u, v, d) for u, v, d in G.edges(data=True) if d.get("confidence") == "AMBIGUOUS"]
    if ambiguous:
        lines += ["", "## Ambiguous Edges - Review These"]
        for u, v, d in ambiguous:
            ul = G.nodes[u].get("label", u)
            vl = G.nodes[v].get("label", v)
            lines += [
                f"- `{ul}` → `{vl}`  [AMBIGUOUS]",
                f"  {d.get('source_file', '')} · relation: {d.get('relation', 'unknown')}",
            ]

    # --- Gaps section ---
    from .analyze import _is_file_node, _is_concept_node

    isolated = [
        n for n in G.nodes()
        if G.degree(n) <= 1 and not _is_file_node(G, n) and not _is_concept_node(G, n)
    ]
    thin_communities = {
        cid: nodes for cid, nodes in communities.items() if len(nodes) < 3
    }
    gap_count = len(isolated) + len(thin_communities)

    if gap_count > 0 or amb_pct > 20:
        lines += ["", "## Knowledge Gaps"]
        if isolated:
            isolated_labels = [G.nodes[n].get("label", n) for n in isolated[:5]]
            suffix = f" (+{len(isolated)-5} more)" if len(isolated) > 5 else ""
            lines.append(f"- **{len(isolated)} isolated node(s):** {', '.join(f'`{l}`' for l in isolated_labels)}{suffix}")
            lines.append("  These have ≤1 connection - possible missing edges or undocumented components.")
        if thin_communities:
            for cid, nodes in thin_communities.items():
                label = community_labels.get(cid, f"Community {cid}")
                node_labels = [G.nodes[n].get("label", n) for n in nodes]
                lines.append(f"- **Thin community `{label}`** ({len(nodes)} nodes): {', '.join(f'`{l}`' for l in node_labels)}")
                lines.append("  Too small to be a meaningful cluster - may be noise or needs more connections extracted.")
        if amb_pct > 20:
            lines.append(f"- **High ambiguity: {amb_pct}% of edges are AMBIGUOUS.** Review the Ambiguous Edges section above.")

    if suggested_questions:
        lines += ["", "## Suggested Questions"]
        no_signal = len(suggested_questions) == 1 and suggested_questions[0].get("type") == "no_signal"
        if no_signal:
            lines.append(f"_{suggested_questions[0]['why']}_")
        else:
            lines.append("_Questions this graph is uniquely positioned to answer:_")
            lines.append("")
            for q in suggested_questions:
                if q.get("question"):
                    lines.append(f"- **{q['question']}**")
                    lines.append(f"  _{q['why']}_")

    return "\n".join(lines)
