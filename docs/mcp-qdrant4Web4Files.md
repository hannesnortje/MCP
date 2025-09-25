F**ull project description** with:

* Qdrant as **the truth**

* MCP server as the **interface** in Cursor

* **Write-through export** (local \+ GitHub, always dual-link format)

* **Crawler** for initial import/bootstrap or legacy sync

* **Dual-link rule** (each exported `.md` always has both GitHub \+ local links, and those links are also stored in Qdrant for graph resolution).

---

# **📘 Project Description — MCP \+ Qdrant Memory with Dual-Link Markdown**

## **🎯 Goal**

Provide an MCP server for Cursor that manages all knowledge (docs, code notes, workflows, etc.) with **Qdrant as the sole source of truth**.

* All content is stored in Qdrant (`documents`, `doc_versions`, `chunks`).

* `.md` files in local repo \+ GitHub are **write-through mirrors** of Qdrant.

Every `.md` file written to disk or GitHub always includes **dual links**:

 \[GitHub\](https://github.com/org/repo/blob/\<commit\>/path/to/file.md) | \[Local\](./path/to/file.md)

*   
* A **crawler** is provided to import existing `.md` seeds (e.g., `README.md` → linked docs) into Qdrant.

---

## **🧠 Architecture**

### **1\. Qdrant Collections**

* **`documents`**

  * Holds latest authoritative version.

  * Payload:

    * `doc_id` (UUID, primary key)

    * `title`

    * `full_md` (entire content)

    * `version` (monotonic int)

    * `tags`

    * `aliases`: `{ "github": [urls], "local": [paths] }`

    * `links_out`: array of internal URIs (`doc://<doc_id>`)

    * `links_dual`: array of `{ github_url, local_path }` extracted from dual-links

    * `created_at`, `updated_at`

* **`doc_versions`**

  * Immutable history of all versions.

  * Payload: `doc_id`, `version`, `full_md`, `change_note`, `aliases_snapshot`, `links_out_snapshot`, timestamps.

* **`chunks`**

  * Semantic retrieval index.

  * Each point \= chunk embedding of one version.

  * Payload: `doc_id`, `version`, `chunk_ix`, `plain_text`, `snippet_md`, `headings`, `tags`.

---

### **2\. MCP Server (Cursor Integration)**

Exposes tools agents can call:

* `memory.doc.create`  
   Create new doc in Qdrant. Export `.md` with dual-links to local \+ GitHub.

* `memory.doc.update`  
   Update existing doc (new version). Export updated `.md` with dual-links.

* `memory.doc.get`  
   Fetch authoritative doc from Qdrant.

* `memory.search`  
   Hybrid search: vector \+ keyword rerank.

* `memory.graph.links`  
   Return outbound \+ inbound links for navigation.

* `memory.import`  
   Run the **crawler** starting from a seed file (`README.md` or GitHub URL). Import all linked `.md` docs into Qdrant.

* `backup.export`  
   Manual full export of Qdrant docs to repo/GitHub (safety net).

---

### **3\. Write-Through Export with Dual Links**

Whenever a doc is created/updated:

1. **Qdrant write**: store new version in `documents` \+ `doc_versions`, reindex `chunks`.

2. **Export**:

   * Save `.md` to `export_path` in repo.

Prepend a **dual-link header**:

 \[GitHub\](https://github.com/org/repo/blob/\<commit\>/docs/pdca/overview.md) | \[Local\](./docs/pdca/overview.md)

\# PDCA Overview  
...

*   
  * Commit \+ push to GitHub.

3. **Aliases updated** in Qdrant: `aliases.local=[path]`, `aliases.github=[url]`.

4. **links\_dual** recorded for link resolution.

---

### **4\. Crawler (Bootstrap / Legacy Sync)**

**Purpose:** Import all existing `.md` into Qdrant by crawling links.

1. Start from `README.md` (local or GitHub).

2. Extract links:

   * If **dual-link row** (`[GitHub](url) | [Local](path)`):

     * Record both in `aliases`.

     * Store in Qdrant as `links_dual`.

   * If single `.md` link: record as raw, resolve later.

3. Create Qdrant documents for each `.md`.

4. After all imported, resolve links into internal URIs (`doc://doc_id`).

This makes all existing `.md` knowledge part of Qdrant. Afterward, all future writes flow through MCP.

---

## **🔄 Data Flows**

### **New Knowledge**

* Agent → `memory.doc.create`

* Qdrant write → chunks → export `.md` with dual links → commit/push → aliases updated

### **Update Knowledge**

* Agent → `memory.doc.update(prev_version=N)`

* Qdrant version++ → reindex chunks → overwrite `.md` with dual links → commit/push → aliases updated

### **Retrieve Knowledge**

* Agent → `memory.search` → top chunks

* Agent → `memory.doc.get(doc_id)` → authoritative Markdown

### **Import Existing Knowledge**

* Agent → `memory.import { seed:"README.md" }`

* Crawler BFS through `.md` links → Qdrant ingest → dual-links preserved → links resolved

---

## **⚙️ Guarantees**

* **Qdrant \= truth**.

* `.md` files \= mirrors with **dual-link headers**.

* **Immutable history** in `doc_versions`.

* **Conflict-safe updates** (require `prev_version`).

* **Hybrid search** (BM25 \+ embeddings).

* **Graph navigation** (links\_out/in).

* **Backup/export** to keep local/GitHub up to date even if retries needed.

---

## **📂 Example Repo Export**

/docs/  
  pdca/overview.md  
  cmmi/template.md  
  knowledge/index.md

Each file starts like:

\[GitHub\](https://github.com/org/repo/blob/abc123/docs/pdca/overview.md) | \[Local\](./docs/pdca/overview.md)

\# PDCA Overview  
This document describes the PDCA workflow...

---

## **🚀 Typical Workflow in Cursor**

1. **Create doc**  
    → `memory.doc.create { title, md, tags, export:true, export_path:"docs/pdca/overview.md" }`  
    → File written locally \+ GitHub with dual-link header

2. **Update doc**  
    → `memory.doc.update { doc_id, prev_version, md, change_note, export:true, export_path:"docs/pdca/overview.md" }`  
    → New version in Qdrant, updated `.md` committed

3. **Import legacy**  
    → `memory.import { seed:"README.md" }`  
    → Crawler follows all links, imports into Qdrant, dual-links stored

4. **Search & navigate**  
    → `memory.search { q:"PDCA template" }`  
    → `memory.graph.links { doc_id }`

---

✅ In short:

* **Qdrant is the living memory**.

* **MCP server is the only interface** for agents.

* **.md files are always written with dual links**, mirrored to GitHub \+ local repo.

* **Crawler seeds the system** with existing `.md`, preserving dual-link info.

