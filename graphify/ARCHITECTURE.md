# 架构

graphify 是一个 Claude Code 技能，底层由 Python 库支撑。技能负责编排库；库也可以独立使用。

## Pipeline

```
detect()  →  extract()  →  build_graph()  →  cluster()  →  analyze()  →  report()  →  export()
```

每个阶段都是一个独立的函数，位于各自的模块中。模块之间通过纯 Python 字典和 NetworkX 图进行通信 — 没有共享状态，除了 `graphify-out/` 目录外没有副作用。

## graphify 全部文件清单

| 模块 | 函数 | 输入 → 输出 | 说明 |
|--------|----------|----------------|------|
| `__init__.py` | 懒加载 API | — | 延迟导入公共函数（extract、build_from_json、cluster、god_nodes、to_json 等），避免提前加载重依赖 |
| `__main__.py` | `main()` | CLI 参数 → 执行命令 | CLI 入口：install、build、query、path、explain、add、watch、update、cluster-only、hook、benchmark 等命令 |
| `detect.py` | `collect_files(root)` | 目录 → `[Path]` | 文件发现：扫描目录、按扩展名过滤、统计词数、生成文件清单 |
| `extract.py` | `extract(path)` | 文件路径 → `{nodes, edges}` | AST 结构提取：使用 tree-sitter 解析 20+ 语言，提取类、函数、调用、导入关系 |
| `build.py` | `build_from_json()`, `build()` | 提取字典 → `nx.Graph` | 图构建：将多个提取结果合并为 NetworkX 图，支持有向/无向图 |
| `cluster.py` | `cluster(G)`, `cohesion_score(G)` | 图 → 带 community 属性的图 | 社区检测：Leiden 算法聚类 + 内聚度评分 |
| `analyze.py` | `analyze(G)`, `god_nodes()`, `surprising_connections()`, `suggest_questions()` | 图 → 分析字典 | 图分析：识别上帝节点、意外连接、建议问题、图谱差异对比 |
| `report.py` | `render_report(G, analysis)`, `generate()` | 图 + 分析 → Markdown | 报告生成：生成 GRAPH_REPORT.md 包含社区结构、关键节点、意外连接 |
| `export.py` | `to_json()`, `to_html()`, `to_svg()`, `to_canvas()`, `to_obsidian()` | 图 → 文件 | 多格式导出：JSON、交互式 HTML、SVG、Obsidian 仓库、Canvas、GraphML、Neo4j Cypher |
| `ingest.py` | `ingest(url)` | URL → 文件 | URL 摄取：从 YouTube、arXiv、PDF、网页等下载内容到语料库 |
| `cache.py` | `check_semantic_cache()`, `save_semantic_cache()` | 文件 → 缓存操作 | 提取缓存：SHA256 哈希缓存机制，跳过未变更文件的重复提取 |
| `security.py` | `validate_url()`, `safe_fetch()`, `sanitize_label()` | 外部输入 → 验证后输出 | 安全验证：URL 校验、文件大小限制、标签清理、路径验证 |
| `validate.py` | `validate_extraction(data)` | 提取字典 → 错误列表 | 模式验证：检查提取结果是否符合 nodes/edges 模式规范 |
| `serve.py` | `start_server(graph_path)` | 图路径 → MCP 服务 | MCP stdio 服务器：提供 query_graph、get_node、shortest_path 等工具 |
| `watch.py` | `watch(root)`, `_rebuild_code()` | 目录 → 变更监听 | 文件监听：watchdog 监听代码变更自动重建图谱 |
| `hooks.py` | `install()`, `uninstall()`, `status()` | — → git hook 操作 | Git Hook 管理：安装/卸载 post-commit 和 post-checkout hook |
| `benchmark.py` | `run_benchmark(graph_path)` | 图文件 → 性能数据 | 基准测试：对比语料库与子图的 token 消耗，验证图谱效率 |
| `transcribe.py` | `transcribe()`, `transcribe_all()` | 视频/音频路径 → 文本 | 音视频转录：faster-whisper 转录 + yt-dlp 下载音频 |
| `wiki.py` | `to_wiki(G, out_dir)` | 图 → Wiki 文件 | Wiki 生成：为每个社区生成独立文章和索引 |
| `manifest.py` | `save_manifest()`, `load_manifest()`, `detect_incremental()` | — → 文件清单 | 增量更新：跟踪已处理文件，支持增量图谱更新 |

## Skill 文件清单

Skill 是面向不同 AI 编程助手的指令文件，通过 `graphify install --platform <平台>` 安装到对应平台。
每个 skill 文件定义了 AI 代理执行 `/graphify` 命令时的完整操作流程。

### 主 Skill 文件结构（以 skill.md 为例）

| 文件 | 目标平台 | 说明 |
|--------|----------|------|
| `skill.md` | Claude Code / Antigravity | 主 Skill，定义完整 `/graphify` 编排流程 |
| `skill-codex.md` | OpenAI Codex CLI | Codex 适配版本 |
| `skill-opencode.md` | OpenCode | OpenCode 适配版本 |
| `skill-aider.md` | Aider | Aider 适配版本 |
| `skill-copilot.md` | GitHub Copilot CLI | Copilot 适配版本 |
| `skill-claw.md` | OpenClaw | OpenClaw 适配版本 |
| `skill-windows.md` | Windows (通用) | Windows 平台适配 |
| `skill-droid.md` | Factory Droid | Droid 适配版本 |
| `skill-trae.md` | Trae | Trae 适配版本 |
| `skill-kiro.md` | Kiro | Kiro 适配版本 |

### Skill 内部流程

每个 Skill 文件定义了 **9 步顺序执行流程**，AI 代理按步骤执行：

| 步骤 | 名称 | 功能 |
|------|------|------|
| Step 1 | 安装检查 | 确保 graphify Python 包可用，记录解释器路径 |
| Step 2 | 文件发现 | 调用 `detect()` 扫描目录，统计文件类型和词数 |
| Step 2.5 | 音视频转录 | 如有视频文件，用 Whisper 转录为文本（可选） |
| Step 3 | 提取实体与关系 | AST 结构提取（免费）+ LLM 语义提取（并行子代理） |
| Step 3A | AST 提取 | tree-sitter 解析代码，提取类/函数/调用关系 |
| Step 3B | 语义提取 | 分发多个 general-purpose 子代理并行处理文档/论文/图片 |
| Step 3C | 合并结果 | AST + 语义结果去重合并 |
| Step 4 | 建图聚类 | 构建 NetworkX 图 → Leiden 聚类 → 分析上帝节点/意外连接 → 生成报告 |
| Step 5 | 社区标注 | AI 为每个社区起 2-5 词的人类可读名称，重新生成报告 |
| Step 6 | 可视化 | 生成 Obsidian 仓库（可选）+ 交互式 HTML |
| Step 7 | 高级导出 | Neo4j Cypher / SVG / GraphML / MCP 服务器（按标志启用） |
| Step 8 | Token 基准测试 | 对比图谱 vs 全语料库的 token 消耗（词数 > 5000 时） |
| Step 9 | 清理报告 | 保存文件清单、更新成本跟踪、输出最终结果 |

### 核心设计原则

1. **持久化图谱** — 关系存储在 `graphify-out/graph.json`，跨会话保留
2. **诚实的审计追踪** — 每条边标记 EXTRACTED（明确）、INFERRED（推导）或 AMBIGUOUS（不确定）
3. **跨文档发现** — 社区检测发现不同文件间的意外连接
4. **并行子代理** — 语义提取阶段使用多个 general-purpose 子代理并行处理，每个处理 20-25 个文件
5. **缓存机制** — SHA256 文件哈希缓存，跳过未变更文件
6. **Deep Mode** — `--mode deep` 标志启用更激进的 INFERRED 边提取

## 提取输出模式

每个提取器返回：

```json
{
  "nodes": [
    {"id": "unique_string", "label": "人类可读名称", "source_file": "路径", "source_location": "L42"}
  ],
  "edges": [
    {"source": "id_a", "target": "id_b", "relation": "calls|imports|uses|...", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS"}
  ]
}
```

`validate.py` 会在 `build_graph()` 消费之前强制检查此模式。

## 置信度标签

| 标签 | 含义 |
|-------|---------|
| `EXTRACTED` | 关系在源码中明确存在（例如 import 语句、直接调用） |
| `INFERRED` | 关系是合理推导（例如调用图第二轮、上下文共现） |
| `AMBIGUOUS` | 关系不确定；在 GRAPH_REPORT.md 中标记供人工审查 |

## 添加新的语言提取器

1. 在 `extract.py` 中添加 `extract_<lang>(path: Path) -> dict` 函数，遵循现有模式（tree-sitter 解析 → 遍历节点 → 收集 `nodes` 和 `edges` → 第二轮调用图生成 INFERRED `calls` 边）。
2. 在 `extract()` 分发逻辑和 `collect_files()` 中注册该文件后缀。
3. 在 `detect.py` 的 `CODE_EXTENSIONS` 和 `watch.py` 的 `_WATCHED_EXTENSIONS` 中添加该后缀。
4. 将 tree-sitter 包添加到 `pyproject.toml` 的依赖中。
5. 在 `tests/fixtures/` 中添加一个示例文件，并在 `tests/test_languages.py` 中添加测试。

## 安全

所有外部输入在使用前都经过 `graphify/security.py` 验证：

- URL → `validate_url()`（仅允许 http/https）+ `_NoFileRedirectHandler`（阻止 file:// 重定向）
- 获取的内容 → `safe_fetch()` / `safe_fetch_text()`（大小上限、超时）
- 图文件路径 → `validate_graph_path()`（必须在 `graphify-out/` 内）
- 节点标签 → `sanitize_label()`（去除控制字符、最长 256 字符、HTML 转义）

完整威胁模型参见 `SECURITY.md`。

## 测试

`tests/` 下每个模块对应一个测试文件。运行方式：

```bash
pytest tests/ -q
```

所有测试都是纯单元测试 — 无网络调用、无 `tmp_path` 之外的文件系统副作用。