# MCP Server with Qdrant Memory — Implementation Plan (v0.4, 2025-09-21)

> MCP server for Cursor with Qdrant vector DB memory. Implements **Tools, Resources, and Prompts** from the start. Memory is layered (Global, Learned, Agent-Specific). Markdown ingestion is optimized and duplicate-safe. Agents are initialized flexibly with a generalized startup prompt. Enhanced for error handling, scalability, and testing.

---

## 1) Scope

- **Server:** Basic, **no UI**, exposes **MCP Tools, Resources, and Prompts** from the start.
- **Markdown-first ingestion:** `.md` files are added to memory **only after optimization** and **duplicate checks** to ensure high-signal storage.
- **Agent-aware memory access:**
  - **Global Memory:** Shared across all agents (e.g., architecture, standards).
  - **Learned Memory:** Lessons and anti-patterns; configurable per agent via `memory_layers`.
  - **Agent-Specific Memory:** Private per agent, isolated storage.
- Production-safe defaults; configurable via `config.yaml`.
- **New in v0.4:** Robust error handling (e.g., Qdrant failures), scalability notes, and expanded testing requirements.

---

## 2) Memory Model (Qdrant Collections)

- `global_memory` — Shared `.md` context (e.g., architecture, conventions).
- `learned_memory` — Lessons, postmortems, anti-patterns for avoiding mistakes.
- `agent_<id>` — Private agent memory for context and actions.
- `file_metadata` — Provenance (path, hash, chunk IDs, memory target, timestamps).
- `policy_memory` — Semantic policy rule storage with version tracking for governance.

**Vector config (defaults):**
- Embeddings: `intfloat/e5-base-v2` (768 dimensions, cosine distance).
- Chunking: 900 tokens target, 200 token overlap, header-aware.
- Deduplication: Cosine similarity ≥ 0.85 (configurable).
- **New in v0.4:** Optional sharding for large collections; retry logic for embedding failures.

---

## 3) Tools (MCP)

### Ingestion & Processing
- `scan_workspace_markdown(directory="./")` — List `.md` files, suggest memory layers via heuristics.
- `analyze_markdown_content(content)` — Detect type/topics/tags, recommend memory layer.
- `optimize_content_for_storage(content, memory_type)` — Clean (preserve headers/code/lists), remove noise (badges, empty sections), add metadata.
- `validate_and_deduplicate(content, memory_type, agent_id?)` — Check similarity, decide skip/merge/update.
- `process_markdown_file(path, memory_type, agent_id?)` — Read → clean → chunk → dedupe → embed → upsert (+ update `file_metadata`).
- `batch_process_markdown_files(assignments)` — Bulk ingestion with per-file diagnostics.

### Agent & Context
- `initialize_new_agent(agent_id, agent_role, memory_layers)` — Create agent with specified memory access.
- `configure_agent_permissions(agent_id, config)` — Set read/write access for memory layers.
- `query_memory_for_agent(agent_id, query, memory_layers)` — Search across allowed layers, return ranked results.
- `store_agent_action(agent_id, action, context, outcome, learn?)` — Log action; optionally upsert to `learned_memory`.

### Policy & Governance
- `build_policy_from_markdown(directory, policy_version, activate)` — Parse policy files, validate rules, create canonical JSON.
- `get_policy_rulebook(version?)` — Retrieve canonical policy JSON with hash verification.
- `validate_json_against_schema(schema_name, candidate_json)` — Enforce required sections per policy.
- `log_policy_violation(agent_id, rule_id, context)` — Track policy compliance issues.

**New in v0.4:**
- All tools include error handling (e.g., Qdrant connection errors, invalid inputs).
- Tools return JSON with `status`, `diagnostics`, `decisions` (e.g., `"deduped": true`), and `ids` (Qdrant points).

---

## 4) Resources (MCP)

Read-only snapshots for agents/IDE:
- `agent_registry` — List of agents (ID, role, memory layers).
- `memory_access_matrix` — Agent-to-memory access mappings.
- `global_memory_catalog` — Indexed global memory chunks with tags.
- `learned_patterns_index` — Lessons categorized by type.
- `agent_memory_summary/{agent_id}` — Per-agent memory digest.
- `file_processing_log` — Ingestion history (file, status, chunk IDs).
- `workspace_markdown_files` — Discovered `.md` files with analysis.
- `memory_collection_health` — Qdrant stats (point count, duplicates, shard status).
- `policy_rulebook` — Canonical JSON policy with version/hash for compliance.
- `policy_violations_log` — Policy violation tracking and audit trail.

**New in v0.4:** Resources support pagination for large datasets; health includes shard diagnostics.

---

## 5) Prompts (MCP)

### Core Prompt
**`agent_startup`**
- **Arguments:**
  - `agent_id` (string, required) — Unique identifier.
  - `agent_role` (string, required) — Role description.
  - `memory_layers` (array, default `["global"]`) — Layers to access (`global`, `learned`, `agent_specific`).
  - `policy_version` (string, required) — Policy version to bind agent to.
  - `policy_hash` (string, required) — SHA-256 hash of policy for verification.
- **Behavior:** Initialize agent, set permissions, preload specified memory layers, bind to policy.
- **Example:**
  ```json
  {
    "prompt": "agent_startup",
    "arguments": {
      "agent_id": "qa_01",
      "agent_role": "Human tester simulating end-user behavior",
      "memory_layers": ["global", "agent_specific"]
    }
  }
  ```

### Optional Aliases
- `development_agent_startup` → `agent_startup(memory_layers=["global", "learned", "agent_specific"])`
- `testing_agent_startup` → `agent_startup(memory_layers=["global", "agent_specific"])`

### Guidance Prompts
- `agent_memory_usage_patterns` — Querying and storing in memory layers.
- `context_preservation_strategy` — Maintaining task continuity.
- `memory_query_optimization` — Crafting effective queries.
- `markdown_optimization_rules` — Cleaning Markdown for storage.
- `memory_type_selection_criteria` — Choosing memory layers.
- `duplicate_detection_strategy` — Deduplication logic and thresholds.

**New in v0.4:** Prompts include error messages for invalid inputs (e.g., unknown `memory_layers`).

---

## 6) Workflows

### Markdown Upload
1. **Discover:** `scan_workspace_markdown()` → List `.md` files.
2. **Analyze:** `analyze_markdown_content()` → Recommend memory layer.
3. **Optimize:** `optimize_content_for_storage()` → Clean content.
4. **Chunk:** Internal helper (900 tokens, header-aware).
5. **Deduplicate:** `validate_and_deduplicate()` → Cosine similarity check.
6. **Store:** `process_markdown_file()` → Embed, upsert to Qdrant.
7. **Log:** Update `file_metadata`, `file_processing_log`.

### Agent Creation
1. **Create:** `initialize_new_agent()` → Set up `agent_<id>` collection.
2. **Configure:** `agent_startup` prompt → Specify role, `memory_layers`.
3. **Permissions:** `configure_agent_permissions()` → Apply access rules.
4. **Operate:** `query_memory_for_agent()` → Search allowed layers.
5. **Learn:** `store_agent_action(learn=true)` → Add to `learned_memory` (if permitted).

**New in v0.4:** Workflows log errors (e.g., failed upserts) to `file_processing_log` or `agent_memory_summary`.

---

## 7) Success Criteria

- Server runs with **Tools, Resources, and Prompts** fully implemented.
- Agents initialized via `agent_startup` with correct memory layer access.
- Markdown ingestion is optimized, duplicate-free, and logged.
- Resources reflect live state (e.g., `agent_registry`, `memory_collection_health`).
- Error handling ensures graceful recovery from Qdrant or input failures.
- Scalability supports at least 10,000 Markdown files and 100 agents.

---

## 8) Implementation Tasks

### Day 1: Core Ingestion
- [ ] Bootstrap Qdrant collections (`global_memory`, `learned_memory`, `agent_*`, `file_metadata`) with sharding support.
- [ ] Implement ingestion tools: `process_markdown_file`, `optimize_content_for_storage`, `validate_and_deduplicate`.
- [ ] Add `batch_process_markdown_files` and `file_processing_log`.
- [ ] Test: Ingest sample repo, verify deduplication, metadata, and error handling.

### Day 2: Agent & Prompts
- [ ] Implement agent tools: `initialize_new_agent`, `configure_agent_permissions`, `query_memory_for_agent`, `store_agent_action`.
- [ ] Implement `agent_startup` prompt with alias shortcuts.
- [ ] Test: Create agents with varied `memory_layers`, verify query routing and action logging.

### Day 3: Resources, Prompts, & Packaging
- [ ] Implement Resources: `agent_registry`, `memory_access_matrix`, `global_memory_catalog`, etc.
- [ ] Add guidance prompts: `agent_memory_usage_patterns`, `markdown_optimization_rules`, etc.
- [ ] Package server: Create `mcp.json`, FastAPI/Flask entrypoint, load `config.yaml`.
- [ ] Test: End-to-end workflow (ingest → initialize → query), resource accuracy, prompt validation.

**New in v0.4:** Add integration tests for error cases (e.g., Qdrant downtime, invalid `memory_layers`).

---

## 9) Configuration (defaults)

```yaml
embeddings:
  model: intfloat/e5-base-v2
  batch_size: 32
  retry_attempts: 3
  retry_delay: 2 # seconds

chunking:
  target_tokens: 900
  overlap_tokens: 200
  header_aware: true

dedupe:
  threshold: 0.85
  near_miss_window: [0.80, 0.85]
  policy: skip_if_duplicate

permissions:
  defaults:
    global: read
    learned: read_write
    agent_specific: read_write

scalability:
  max_points_per_collection: 100000
  shards_per_collection: 2

policy:
  directory: "./policy"
  version: "v1.0"
  fail_on_duplicate_rule_id: true
  fail_on_missing_rule_id: true
  compute_hash_from: "canonical_json"
  activate_on_build: true
```

**New in v0.4:** Added `retry_attempts`, `retry_delay` for embeddings, and `scalability` section for large datasets.

---

## 10) Risks & Mitigations

- **Markdown cleanup errors** → Use conservative rules, test with round-trip fixtures.
- **Dedup false positives/negatives** → Log near-misses (0.80-0.85), allow threshold tuning.
- **Memory routing errors** → Test all `memory_layers` combinations, use `memory_access_matrix` as truth.
- **Qdrant failures** → Implement retries, fallback to error logs in `file_processing_log`.
- **Scalability limits** → Enable sharding, monitor `memory_collection_health` for bottlenecks.

---

## 11) Previous Version (archived)

<details>
<summary>Show v0.3</summary>

# MCP Server with Qdrant Memory — Implementation Plan (v0.3, 2025-09-21)

> MCP server for Cursor with Qdrant vector DB memory. Implements **Tools, Resources, and Prompts** from the start. Memory is layered (Global, Learned, Agent-Specific). Markdown ingestion is optimized and duplicate-safe. Agents can be initialized flexibly with general startup prompts.

---

## 1) Scope

- **Server:** basic, **no UI**, and exposes **MCP Tools + Resources + Prompts from the start**.
- **Markdown-first ingestion:** `.md` files are added to memory **only after optimization** and **duplicate checks** to avoid clutter.
- **Agent-aware memory access:**
  - **Global Memory:** shared across all agents.
  - **Learned Memory:** stores lessons; can be **included or excluded per agent**.
  - **Agent-Specific Memory:** private to the agent.
- Production-safe defaults; configurable via `config.yaml`.

---


## 2) Memory Model (Qdrant Collections)

- `global_memory` — shared `.md` context.
- `learned_memory` — accumulated lessons.
- `agent_<id>` — private agent memory.
- `file_metadata` — provenance (path, hash, chunk ids, memory target).

**Vector config (defaults):**
- Embeddings: `intfloat/e5-base-v2`
- Chunking: 900 tokens target, 200 overlap, header-aware
- Deduplication: cosine ≥ 0.85

---

## 3) Tools (MCP)

- `scan_workspace_markdown(directory="./")` — list `.md` files + suggest memory.
- `analyze_markdown_content(content)` — detect type/topics/tags + recommended memory.
- `optimize_content_for_storage(content, memory_type)` — cleanup + metadata.
- `validate_and_deduplicate(content, memory_type, agent_id)` — prevent duplicates.
- `process_markdown_file(path, memory_type, agent_id?)` — clean → dedupe → embed → upsert.
- `batch_process_markdown_files(assignments)` — bulk ingestion.
- `initialize_new_agent(agent_id, agent_role, memory_layers)` — create agent with declared memory layers.
- `configure_agent_permissions(agent_id, config)` — fine-tune allowed access.
- `query_memory_for_agent(agent_id, query, memory_layers)` — query through declared memories.
- `store_agent_action(agent_id, action, context, outcome, learn?)` — log + optional learned memory.

---

## 4) Resources (MCP)

Read-only snapshots for agents/IDE:  
- `agent_registry`  
- `memory_access_matrix`  
- `global_memory_catalog`  
- `learned_patterns_index`  
- `agent_memory_summary/{agent_id}`  
- `file_processing_log`  
- `workspace_markdown_files`  
- `memory_collection_health`  

---

## 5) Prompts (MCP)

### Generalized Startup Prompt

**`agent_startup`**  
- **Arguments:**
  - `agent_id` (string) — unique id.  
  - `agent_role` (string) — description of purpose.  
  - `memory_layers` (array, default `[global]`) — which memories to load (`global`, `learned`, `agent_specific`).  

**Example:**  
```json
{
  "prompt": "agent_startup",
  "arguments": {
    "agent_id": "qa_01",
    "agent_role": "Human tester simulating end-user behavior",
    "memory_layers": ["global","agent_specific"]
  }
}
```

### Optional Aliases (shortcuts)
- `development_agent_startup` → `agent_startup(memory_layers=["global","learned","agent_specific"])`  
- `testing_agent_startup` → `agent_startup(memory_layers=["global","agent_specific"])`  

### Other Prompts
- `agent_memory_usage_patterns` — guidance on using memory layers.  
- `context_preservation_strategy` — continuity strategies.  
- `memory_query_optimization` — query crafting tips.  
- `markdown_optimization_rules` — how docs should be cleaned.  
- `memory_type_selection_criteria` — global vs learned vs agent.  
- `duplicate_detection_strategy` — dedup rationale.  

---

## 6) Workflows

### Markdown Upload
Scan → Analyze → Optimize → Deduplicate → Embed → Upsert → Update logs/resources.

### Agent Creation
Create agent → Specify role + memory_layers → Initialize → Load chosen memory contexts → Start with `agent_startup` prompt.

---

## 7) Success Criteria

- Server runs with Tools, Resources, and Prompts.  
- Agents initialized via **general `agent_startup`** prompt.  
- Markdown ingestion optimized + deduplicated.  
- Memory access respects `memory_layers`.  
- Resources reflect live memory state.  

---

## 8) Implementation Tasks

### Day 1
- [ ] Bootstrap Qdrant collections (`global_memory`, `learned_memory`, `agent_*`, `file_metadata`).  
- [ ] Implement ingestion pipeline (`process_markdown_file`, `optimize_content_for_storage`, `validate_and_deduplicate`).  
- [ ] Batch ingestion + file log.  

### Day 2
- [ ] Implement agent tools (`initialize_new_agent`, `query_memory_for_agent`, `store_agent_action`).  
- [ ] Implement `agent_startup` prompt.  

### Day 3
- [ ] Add Resources (agent registry, catalogs).  
- [ ] Add other prompts (guidance + ingestion rules).  
- [ ] Package server (`mcp.json`, entrypoint).  

---

## 9) Configuration (defaults)

```yaml
embeddings:
  model: intfloat/e5-base-v2
  batch_size: 32

chunking:
  target_tokens: 900
  overlap_tokens: 200
  header_aware: true

dedupe:
  threshold: 0.85
  near_miss_window: [0.80, 0.85]
  policy: skip_if_duplicate

permissions:
  defaults:
    global: read
    learned: conditional
    agent: read_write
```

---

## 10) Risks & Mitigations

- **Markdown cleanup over/under-aggressive** → conservative rules, test fixtures.  
- **Dedup errors** → configurable threshold, log near misses.  
- **Memory routing errors** → unit tests with different memory_layers combos.  

---

## 11) Previous Version (archived)

<details>
<summary>Show v0.2</summary>

[Content of v0.2 from previous document, omitted here for brevity]

</details>
</details>