# Generic Memory System Design

## Overview
Replace the rigid `global/learned/agent` memory types with a flexible, user-defined collection system.

## Current Problems
- ❌ Only 3 hardcoded memory types: `global`, `learned`, `agent`
- ❌ Fixed collection names and structures  
- ❌ Rigid API methods tied to specific types
- ❌ No way to create custom collections for different projects/contexts
- ❌ Memory browser locked to predefined types

## Proposed Generic System

### 1. Flexible Collections
```typescript
interface Collection {
    name: string;              // "project-alpha", "meeting-notes", "research"
    description?: string;      // User-provided description
    tags: string[];           // ["work", "personal", "code", "docs"]
    metadata: {
        created_at: string;
        created_by: string;
        permissions: {
            read: string[];    // Users/agents who can read
            write: string[];   // Users/agents who can write
            admin: string[];   // Users/agents who can manage
        };
        category?: string;     // "documentation", "code", "notes", "research"
        project?: string;      // Associated project/context
        retention?: number;    // Days to keep (optional TTL)
    };
    stats: {
        document_count: number;
        last_updated: string;
        size_bytes: number;
    };
}
```

### 2. Generic Memory Operations
```python
# Create collections dynamically
create_collection(name="project-alpha", description="Alpha project notes", tags=["work", "development"])

# Add content to any collection
add_memory(collection="project-alpha", content="...", metadata={...})

# Search across multiple collections  
search_memory(query="bug fix", collections=["project-alpha", "troubleshooting"], limit=10)

# Manage collections
list_collections(filter_by_tags=["work"], owned_by="user123")
update_collection(name="project-alpha", new_tags=["work", "completed"])
delete_collection(name="old-project", confirm=True)
```

### 3. Backward Compatibility Migration
- `global_memory` → `shared-knowledge` collection with tag ["global", "shared"]
- `learned_memory` → `patterns-insights` collection with tag ["learned", "patterns"]  
- `agent_specific_memory_X` → `agent-X-context` collection with tag ["agent", "personal"]

### 4. Enhanced Memory Browser UI
- **Collection Browser**: Tree view of all collections with metadata
- **Dynamic Creation**: "New Collection" button with form
- **Tag Filtering**: Filter collections by tags, owner, project
- **Bulk Operations**: Move content between collections, merge collections
- **Collection Templates**: Quick create from templates (project, research, etc.)

### 5. Smart Collection Suggestions
Based on content analysis, suggest appropriate collection:
- Code snippets → "code-library"
- Meeting notes → "meetings-2024"
- Bug reports → "troubleshooting"
- Documentation → "project-docs"

## Implementation Plan

### Phase 1: Core Infrastructure
1. **New Collection Model**: Replace hardcoded types with dynamic collections
2. **Collection Manager**: CRUD operations for collections
3. **Migration Script**: Convert existing data to new format

### Phase 2: API Updates  
1. **Generic Memory API**: Replace type-specific methods
2. **Flexible Query Engine**: Search across any collections
3. **Permission System**: Collection-level access control

### Phase 3: UI Enhancement
1. **Dynamic Collection Browser**: Show all collections, not just 3 types
2. **Collection Management UI**: Create, edit, delete collections
3. **Smart Content Organization**: Suggest collections based on content

## Benefits
- ✅ **Infinite Flexibility**: Create any collection structure users need
- ✅ **Better Organization**: Group content by project, team, topic, etc.
- ✅ **User-Centric**: Let users define their own memory organization
- ✅ **Scalable**: No limits on number or types of collections
- ✅ **Professional**: Proper permissions, metadata, lifecycle management