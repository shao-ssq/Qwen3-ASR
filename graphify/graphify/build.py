"""将提取的 nodes/edges 字典组装为 NetworkX 图，保留边方向。

核心职责: 将多个提取结果合并为 NetworkX 图（支持有向/无向），处理节点去重和悬空边。

公共方法:
    build_from_json(extraction)  - 从单个提取字典构建图 → nx.Graph | nx.DiGraph
    build(extractions)           - 批量合并多个提取结果为一张图 → nx.Graph | nx.DiGraph

关键设计:
    - 三层节点去重:
        1) 文件内: extract.py 的 seen_ids 集合确保同文件同 ID 只出现一次
        2) 文件间: NetworkX G.add_node() 幂等，后调用的属性覆盖前者
           (语义节点覆盖 AST 节点，语义标签更丰富，AST 位置更精确)
        3) 语义合并: skill 层在调用 build() 前通过 seen 集合合并缓存与新结果
    - 悬空边处理: 外部/标准库导入产生的目标节点不存在时，跳过该边 (非错误)
    - 方向保留: DiGraph 模式下保留 source→target 方向，并在边属性中记录 _src/_tgt
    - 超边支持: extraction 中的 hyperedges 存储在 G.graph["hyperedges"] 属性中
    - 兼容处理: 旧版 NetworkX 用 "links" 代替 "edges"，自动 remap
"""
from __future__ import annotations
import sys
import networkx as nx
from .validate import validate_extraction


def build_from_json(extraction: dict, *, directed: bool = False) -> nx.Graph:
    """Build a NetworkX graph from an extraction dict.

    directed=True produces a DiGraph that preserves edge direction (source→target).
    directed=False (default) produces an undirected Graph for backward compatibility.
    """
    # NetworkX <= 3.1 serialised edges as "links"; remap to "edges" for compatibility.
    if "edges" not in extraction and "links" in extraction:
        extraction = dict(extraction, edges=extraction["links"])
    errors = validate_extraction(extraction)
    # Dangling edges (stdlib/external imports) are expected - only warn about real schema errors.
    real_errors = [e for e in errors if "does not match any node id" not in e]
    if real_errors:
        print(f"[graphify] Extraction warning ({len(real_errors)} issues): {real_errors[0]}", file=sys.stderr)
    G: nx.Graph = nx.DiGraph() if directed else nx.Graph()
    for node in extraction.get("nodes", []):
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    node_set = set(G.nodes())
    for edge in extraction.get("edges", []):
        if "source" not in edge and "from" in edge:
            edge["source"] = edge["from"]
        if "target" not in edge and "to" in edge:
            edge["target"] = edge["to"]
        if "source" not in edge or "target" not in edge:
            continue
        src, tgt = edge["source"], edge["target"]
        if src not in node_set or tgt not in node_set:
            continue  # skip edges to external/stdlib nodes - expected, not an error
        attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
        # Preserve original edge direction - undirected graphs lose it otherwise,
        # causing display functions to show edges backwards.
        attrs["_src"] = src
        attrs["_tgt"] = tgt
        G.add_edge(src, tgt, **attrs)
    hyperedges = extraction.get("hyperedges", [])
    if hyperedges:
        G.graph["hyperedges"] = hyperedges
    return G


def build(extractions: list[dict], *, directed: bool = False) -> nx.Graph:
    """Merge multiple extraction results into one graph.

    directed=True produces a DiGraph that preserves edge direction (source→target).
    directed=False (default) produces an undirected Graph for backward compatibility.

    Extractions are merged in order. For nodes with the same ID, the last
    extraction's attributes win (NetworkX add_node overwrites). Pass AST
    results before semantic results so semantic labels take precedence, or
    reverse the order if you prefer AST source_location precision to win.
    """
    combined: dict = {"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    for ext in extractions:
        combined["nodes"].extend(ext.get("nodes", []))
        combined["edges"].extend(ext.get("edges", []))
        combined["hyperedges"].extend(ext.get("hyperedges", []))
        combined["input_tokens"] += ext.get("input_tokens", 0)
        combined["output_tokens"] += ext.get("output_tokens", 0)
    return build_from_json(combined, directed=directed)
