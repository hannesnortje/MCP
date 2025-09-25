# **📘 Project Description — MCP + Qdrant Reference-Based Document Architecture**

**Full project description** with:

* Qdrant as **the truth** for both memory and document metadata

* **Reference-based documents** - content lives in memory, metadata in documents

* MCP server as the **interface** in Cursor

* **Write-through export** (local + GitHub, always dual-link format)

* **Crawler** for initial import/bootstrap or legacy sync

* **Differential version control** with intelligent chunk updates

* **Dual-link rule** (each exported `.md` always has both GitHub + local links, stored in Qdrant for graph resolution)

---

## **🎯 Goal**

Provide an MCP server for Cursor that manages all knowledge (docs, code notes, workflows, etc.) with **Qdrant as the sole source of truth** using a **reference-based architecture**.

* Document **content** is stored in existing memory collections (`global_memory`, `learned_memory`, `agent_memory_*`)
* Document **metadata** is stored in lightweight reference collections (`documents`, `doc_versions`) 
* `.md` files in local repo + GitHub are **write-through mirrors** of Qdrant content
* **Differential version control** updates only changed content chunks

Every `.md` file written to disk or GitHub always includes **dual links**:

```markdown
[GitHub](https://github.com/org/repo/blob/<commit>/path/to/file.md) | [Local](./path/to/file.md)
```

* A **crawler** is provided to import existing `.md` seeds (e.g., `README.md` → linked docs) into Qdrant
* **Unified search** across both memory and documents using existing infrastructure

---

## **🧠 Architecture**

### **1. Qdrant Collections**

#### **Enhanced Memory Collections** *(existing + new fields)*
* **`global_memory`**, **`learned_memory`**, **`agent_memory_*`**
  * **UNCHANGED**: `content`, `timestamp`, `category`, `importance`, `agent_id`
  * **NEW FIELDS**:
    * `source_doc_id` (UUID, optional) - Which document this chunk came from
    * `source_doc_version` (int, optional) - Which version of the document  
    * `chunk_index` (int, optional) - Position within document (0, 1, 2...)
    * `is_current` (bool, default true) - Is this from current doc version?
    * `content_hash` (string, optional) - SHA-256 of chunk content for change detection

#### **New Document Reference Collections**

* **`documents`** *(lightweight metadata only)*
  * Holds document structure and references - **NO CONTENT**
  * Payload:
    * `doc_id` (UUID, primary key)
    * `title` (string)
    * `version` (monotonic int)
    * `tags` (array of strings)
    * `memory_type` (string) - Which memory collection: "global", "learned", "agent_{id}"
    * `memory_chunk_ids` (array) - References to chunks in memory collections
    * `content_hash` (string) - SHA-256 of full reconstructed content
    * `aliases`: `{ "github": [urls], "local": [paths] }`
    * `links_out`: array of internal URIs (`doc://<doc_id>`)
    * `links_dual`: array of `{ github_url, local_path }` extracted from dual-links
    * `created_at`, `updated_at`

* **`doc_versions`** *(immutable metadata history)*
  * Immutable history of document versions - **NO CONTENT**
  * Payload: 
    * `doc_id` (UUID)
    * `version` (int)
    * `memory_chunk_ids` (array) - Historical chunk references
    * `content_hash` (string) - Hash of content at this version
    * `change_note` (string)
    * `aliases_snapshot`, `links_out_snapshot`, `links_dual_snapshot`
    * `created_at`

---

### **2. MCP Server (Cursor Integration)**

Exposes tools agents can call:

* **`memory.doc.create`**  
   Create new doc metadata in Qdrant. Store content in appropriate memory collection. Export `.md` with dual-links to local + GitHub.

* **`memory.doc.update`**  
   Update existing doc with differential chunk analysis. Only changed chunks are updated/created. Export updated `.md` with dual-links.

* **`memory.doc.get`**  
   Fetch document by reconstructing content from memory chunks. Return full markdown with dual-link headers.

* **`memory.search`** *(enhanced existing tool)*  
   Hybrid search across memory collections with document context. Unified results from both memory + documents.

* **`memory.graph.links`**  
   Return outbound + inbound links for navigation using document metadata.

* **`memory.import`**  
   Run the **crawler** starting from a seed file (`README.md` or GitHub URL). Create document metadata and store content in memory.

* **`backup.export`**  
   Manual full export of all documents (reconstructed from memory) to repo/GitHub.

---

### **3. Reference-Based Content Management**

#### **Document Creation Flow**:
1. **Content Processing**: Split content into semantic chunks
2. **Memory Storage**: Store chunks in appropriate memory collection with document references  
3. **Document Metadata**: Create document record with chunk references
4. **Export**: Generate `.md` file from memory chunks with dual-link header
5. **Git Operations**: Commit + push to GitHub

#### **Document Update Flow** *(Differential)*:
1. **Change Detection**: Compare new content with existing chunks using similarity
2. **Chunk Analysis**: Identify UNCHANGED, MODIFIED, ADDED, DELETED chunks
3. **Memory Updates**:
   - **UNCHANGED**: Update version reference only
   - **MODIFIED**: Mark old chunk as `is_current=false`, create new chunk
   - **DELETED**: Mark old chunk as `is_current=false`
   - **ADDED**: Create new memory chunk
4. **Document Versioning**: Update document metadata, create version record
5. **Export**: Regenerate `.md` file from updated chunks

#### **Content Reconstruction**:
```python
async def reconstruct_document_content(doc_id: str, version: int = None) -> str:
    """Reconstruct full document from memory chunks"""
    doc = await get_document(doc_id)
    
    if version is None:
        # Get current chunks
        chunks = await get_memory_chunks(
            filter={"source_doc_id": doc_id, "is_current": True}
        )
    else:
        # Get historical chunks for specific version
        doc_version = await get_document_version(doc_id, version)
        chunks = await get_memory_chunks(
            ids=doc_version.memory_chunk_ids
        )
    
    # Sort by chunk_index and reconstruct
    sorted_chunks = sorted(chunks, key=lambda x: x.chunk_index)
    full_content = "\n\n".join(chunk.content for chunk in sorted_chunks)
    
    return full_content
```

---

### **4. Write-Through Export with Dual Links**

Whenever a doc is created/updated:

1. **Memory Write**: Store/update content chunks in memory collections with document references

2. **Document Metadata**: Update document record with new chunk references and version

3. **Content Reconstruction**: Rebuild full markdown from current memory chunks

4. **Export**:
   * Save `.md` to `export_path` in repo
   * Prepend **dual-link header**:
     ```markdown
     [GitHub](https://github.com/org/repo/blob/<commit>/docs/pdca/overview.md) | [Local](./docs/pdca/overview.md)
     
     # PDCA Overview
     ...
     ```
   * Commit + push to GitHub

5. **Aliases Updated**: Update `aliases.local=[path]`, `aliases.github=[url]` in document metadata

6. **Link Resolution**: Extract and store `links_dual` for graph navigation

---

### **5. Crawler (Bootstrap / Legacy Sync)**

**Purpose:** Import all existing `.md` into Qdrant using reference-based approach.

1. **Discovery**: Start from `README.md` (local or GitHub), crawl all linked documents

2. **Content Processing**: For each discovered `.md`:
   * Extract content and chunk into semantic pieces
   * Store chunks in appropriate memory collection (global by default)
   * Create document metadata with chunk references

3. **Link Extraction**:
   * If **dual-link row** (`[GitHub](url) | [Local](path)`):
     * Record both in `aliases`
     * Store in document metadata as `links_dual`
   * If single `.md` link: record for later resolution

4. **Link Resolution**: After all documents imported, resolve links into internal URIs (`doc://doc_id`)

5. **Memory Integration**: All document content is now searchable via existing memory search tools

---

## **🔄 Data Flows**

### **New Knowledge**
* Agent → `memory.doc.create`
* Content chunking → Memory storage (with doc references) → Document metadata creation → Export `.md` with dual links → Git commit/push → Aliases updated

### **Update Knowledge**  
* Agent → `memory.doc.update(doc_id, prev_version=N)`
* Differential analysis → Memory chunk updates (UNCHANGED/MODIFIED/ADDED/DELETED) → Document version++ → Content reconstruction → Export updated `.md` → Git commit/push

### **Retrieve Knowledge**
* Agent → `memory.search` → Results from memory collections (enhanced with document context)
* Agent → `memory.doc.get(doc_id)` → Content reconstruction from memory chunks → Full markdown with dual-links

### **Import Existing Knowledge**
* Agent → `memory.import { seed:"README.md" }`
* Crawler BFS through `.md` links → Content chunking → Memory storage → Document metadata creation → Link resolution

### **Unified Search**
* Single search interface across all content (memory + documents)
* Results include both standalone memory items and document chunks
* Document context provided for all results

---

## **⚙️ Guarantees**

* **Qdrant = truth** for both memory and document metadata
* **Content lives in memory** - leverages existing robust infrastructure  
* **Documents are references** - lightweight metadata layer
* **Differential updates** - only changed chunks are modified
* **.md files = mirrors** with **dual-link headers**
* **Immutable history** in `doc_versions` and memory chunk versioning
* **Conflict-safe updates** (require `prev_version`)
* **Unified search** across memory and documents
* **Backward compatibility** - existing memory tools work unchanged
* **Version rollback** - reconstruct any historical version from memory chunks

---

## **💡 Architecture Benefits**

### **Complexity Reduction**
* **No content duplication** - content lives only in memory collections
* **Reuse existing infrastructure** - memory search, policy compliance, embedding generation
* **Simplified schema** - lightweight document metadata vs. full content storage
* **Unified search** - single interface for all content types

### **Performance Advantages**
* **Efficient storage** - no content duplication between memory and documents
* **Fast searches** - leverage existing optimized memory search
* **Incremental updates** - only changed chunks need processing
* **Memory deduplication** - similar content across documents can be deduplicated

### **Operational Benefits**
* **Backward compatibility** - existing memory tools continue working unchanged
* **Gradual adoption** - documents can reference existing memory content
* **Policy compliance** - existing policy system applies to document content
* **Easy migration** - existing memory content can be retroactively organized into documents

---

## **📂 Example Repo Export**

```
/docs/
  pdca/overview.md
  cmmi/template.md  
  knowledge/index.md
```

Each file starts like:
```markdown
[GitHub](https://github.com/org/repo/blob/abc123/docs/pdca/overview.md) | [Local](./docs/pdca/overview.md)

# PDCA Overview
This document describes the PDCA workflow...

## Process Steps
1. Plan: Define objectives and processes
2. Do: Implement the plan
3. Check: Monitor and evaluate
4. Act: Take corrective action
```

**Behind the scenes:**
- Content stored as chunks in `global_memory` with `source_doc_id` references
- Document metadata in `documents` collection with `memory_chunk_ids` array
- Full content reconstructed on-demand from memory chunks

---

## **🚀 Typical Workflow in Cursor**

1. **Create document**  
   → `memory.doc.create { title:"PDCA Overview", content:"# PDCA...", memory_type:"global", export_path:"docs/pdca/overview.md" }`  
   → Content chunked and stored in `global_memory` → Document metadata created → File exported locally + GitHub with dual-link header

2. **Update document**  
   → `memory.doc.update { doc_id, prev_version:1, content:"# PDCA Updated...", change_note:"Added examples" }`  
   → Differential analysis → Only changed chunks updated in memory → New document version → Updated `.md` committed

3. **Search across all content**  
   → `memory.search { q:"PDCA process steps" }`  
   → Returns results from both standalone memory and document chunks → Document context included

4. **Get full document**  
   → `memory.doc.get { doc_id }`  
   → Content reconstructed from memory chunks → Full markdown with dual-links returned

5. **Import legacy content**  
   → `memory.import { seed:"README.md" }`  
   → Crawler discovers linked documents → Content stored in memory → Document metadata created → Dual-links preserved

6. **Navigate document graph**  
   → `memory.graph.links { doc_id }`  
   → Returns linked documents for navigation

---

## **🔧 Implementation Advantages**

### **Development Efficiency**
* **80% code reuse** - leverage existing memory infrastructure
* **Simplified implementation** - reference management vs. full content system
* **Faster development** - estimated 12-14 weeks vs. 20 weeks for full system

### **Migration Strategy**
* **Zero breaking changes** - existing memory tools unchanged
* **Gradual adoption** - users can organize existing memory into documents
* **Backward compatibility** - existing memory content continues to work
* **Clear separation** - memory for raw content, documents for structured knowledge

### **Operational Benefits**
* **Unified search** - single interface for all content discovery
* **Policy compliance** - existing governance applies to document content  
* **Performance optimization** - leverage existing memory search optimizations
* **Storage efficiency** - no content duplication, intelligent deduplication possible

---

✅ **In summary:**

* **Qdrant is the living memory** for both content and document structure
* **Documents are smart references** that organize memory content  
* **MCP server is the only interface** for agents
* **Content lives in memory** - documents provide organization and versioning
* **.md files are always written with dual links**, mirrored to GitHub + local repo
* **Differential updates** ensure efficient version control
* **Unified search** across all content types with document context
* **Backward compatibility** preserves all existing functionality while adding document capabilities