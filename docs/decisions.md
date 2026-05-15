# Rosetta Architectural Decisions
**IBM Bob Hackathon - Technical Decision Log**  
**Purpose**: Document key technical decisions for Bob session report

---

## Decision 1: Multi-Page Streamlit Architecture

**Context**: Need to build a web application with 7 distinct pages for database onboarding.

**Options Considered**:
1. Single-page app with tabs
2. Flask/FastAPI with custom routing
3. Streamlit multi-page native structure

**Decision**: Streamlit multi-page native structure

**Rationale**:
- **Speed**: No routing logic needed, automatic sidebar generation
- **Deployment**: Free Streamlit Community Cloud hosting
- **State Management**: Built-in session state across pages
- **Development**: Each page is independent file, enables parallel development
- **Time Constraint**: 45 hours requires fastest path to working prototype

**Trade-offs**:
- Less control over URL structure
- Limited customization of navigation
- Streamlit-specific patterns (not transferable to other frameworks)

**Impact**: Enables rapid development and free deployment, critical for hackathon timeline

---

## Decision 2: pyodbc for SQL Server Connectivity

**Context**: Need reliable SQL Server connection that works locally and on Streamlit Cloud.

**Options Considered**:
1. `pymssql` - Pure Python, no external dependencies
2. `pyodbc` - ODBC driver wrapper
3. `sqlalchemy` - ORM layer

**Decision**: `pyodbc` with ODBC Driver 17 for SQL Server

**Rationale**:
- **Compatibility**: ODBC Driver 17 pre-installed on Streamlit Cloud
- **SQL Server Native**: Best support for SQL Server-specific features
- **Metadata Access**: Robust access to system tables (INFORMATION_SCHEMA, sys.*)
- **Authentication**: Supports both Windows and SQL Authentication
- **Performance**: Direct driver access, no ORM overhead

**Trade-offs**:
- Requires ODBC driver installation (but available on target platform)
- More verbose connection string syntax
- Less portable to other databases

**Impact**: Ensures deployment success on Streamlit Cloud, critical for demo

---

## Decision 3: streamlit-agraph for Schema Visualization

**Context**: Need interactive graph visualization of 70+ tables with relationships.

**Options Considered**:
1. `pyvis` - Interactive HTML graphs
2. `networkx` + `matplotlib` - Static images
3. `streamlit-agraph` - Streamlit-native graph component
4. `graphviz` - DOT language graphs

**Decision**: `streamlit-agraph` with `graphviz` fallback

**Rationale**:
- **Streamlit Integration**: Built specifically for Streamlit, no iframe hacks
- **Interactivity**: Clickable nodes, zoom/pan, force-directed layout
- **Performance**: Handles 70 nodes without browser lag
- **Distinctive Feature**: Visual appeal critical for hackathon judging
- **Fallback Plan**: If streamlit-agraph fails, graphviz generates clickable SVG

**Trade-offs**:
- Less mature than pyvis (fewer examples)
- Limited layout customization
- Potential deployment issues (hence fallback)

**Impact**: Provides the "wow factor" visual that differentiates Rosetta from text-based tools

---

## Decision 4: Bob API Integration During Introspection

**Context**: Need to generate human-readable documentation from schema metadata.

**Options Considered**:
1. Pre-generated templates (no LLM)
2. LLM generation on-demand per page
3. LLM batch generation during introspection
4. Hybrid: templates + LLM enhancement

**Decision**: LLM batch generation during introspection (3-4 API calls)

**Rationale**:
- **User Experience**: Single loading phase, then instant page navigation
- **Cost Efficiency**: Batch calls cheaper than per-page generation
- **Session Caching**: Generate once, use across all pages
- **Bobcoin Budget**: 4-5 coins per introspection fits within 35-coin budget
- **Quality**: Full context available during generation (better results)

**Trade-offs**:
- Longer initial wait (60 seconds vs instant)
- Cannot regenerate individual sections without full re-introspection
- Higher upfront cost if user disconnects early

**Impact**: Balances cost, performance, and user experience for hackathon demo

---

## Decision 5: Three-Tier Implementation Strategy

**Context**: 45 hours to build, test, and deploy with 35 Bobcoin budget.

**Options Considered**:
1. Build all features, then deploy
2. Deploy minimal version, iterate in production
3. Tiered approach: deploy early, add features incrementally

**Decision**: Three-tier strategy (Tier 1 → deploy → Tier 2 → Tier 3)

**Rationale**:
- **Risk Mitigation**: Early deployment catches Streamlit Cloud issues
- **Demo Safety**: Working prototype guaranteed even if Tier 2/3 incomplete
- **Feedback Loop**: Can test with real users after Tier 1
- **Budget Control**: Can stop at Tier 2 if Bobcoins run low
- **Parallel Work**: Can polish Tier 1 while building Tier 2

**Tier Breakdown**:
- **Tier 1** (20h, 10 coins): Core pages + deployment
- **Tier 2** (15h, 15 coins): Interactive features (Schema Map, queries)
- **Tier 3** (10h, 10 coins): Polish and production-ready

**Trade-offs**:
- More deployment overhead (3 deploys vs 1)
- Potential rework if architecture changes
- Users see incomplete features temporarily

**Impact**: Maximizes chance of working demo, critical for hackathon success

---

## Decision 6: Session State for Data Caching

**Context**: Need to avoid re-querying database on every page navigation.

**Options Considered**:
1. Re-query database on each page load
2. Cache in browser localStorage
3. Streamlit session state
4. External cache (Redis, etc.)

**Decision**: Streamlit session state

**Rationale**:
- **Built-in**: No external dependencies
- **Persistence**: Survives page navigation within session
- **Simplicity**: Direct Python dict access
- **Security**: Data stays server-side, not exposed to browser
- **Cost**: No additional infrastructure

**Trade-offs**:
- Lost on browser refresh (acceptable for demo)
- Memory usage per session (limited by Streamlit Cloud)
- No cross-session sharing

**Impact**: Enables fast page navigation, critical for user experience

---

## Decision 7: Read-Only Query Execution

**Context**: Allow users to run sample queries, but prevent data modification.

**Options Considered**:
1. Full SQL access (trust users)
2. Whitelist specific queries only
3. Read-only validation (reject DML/DDL)
4. Separate read-only database user

**Decision**: Read-only validation in query executor

**Rationale**:
- **Security**: Prevents accidental/malicious data modification
- **Flexibility**: Users can modify sample queries (learning tool)
- **Simplicity**: No need for separate database user
- **Demo Safety**: AdventureWorks data stays intact

**Validation Rules**:
- Reject: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`, `TRUNCATE`
- Allow: `SELECT`, `WITH` (CTEs), `EXPLAIN`
- Timeout: 30 seconds max
- Row limit: 1000 rows max

**Trade-offs**:
- Regex validation can be bypassed (not foolproof)
- Limits advanced users who want to test writes
- Doesn't prevent expensive queries (only timeout helps)

**Impact**: Balances security and flexibility for demo environment

---

## Decision 8: Markdown Export Format

**Context**: Need to provide downloadable documentation for offline use.

**Options Considered**:
1. PDF generation (reportlab, weasyprint)
2. HTML export
3. Markdown export
4. JSON export

**Decision**: Markdown export

**Rationale**:
- **Simplicity**: No complex rendering, just text formatting
- **Portability**: Readable in any text editor, GitHub, Obsidian, etc.
- **Version Control**: Diffable, can track changes
- **No Dependencies**: Pure Python string formatting
- **Developer Friendly**: Target audience prefers Markdown

**Trade-offs**:
- No visual formatting (tables, colors)
- Schema Map becomes text description (not visual)
- Less "polished" than PDF

**Impact**: Fast to implement, fits developer workflow

---

## Decision 9: Anthropic SDK for LLM Integration

**Context**: Need to call Bob/Claude API for content generation.

**Options Considered**:
1. `anthropic` Python SDK
2. `requests` with custom API calls
3. `langchain` framework
4. `openai` SDK (if Bob supports OpenAI format)

**Decision**: `anthropic` Python SDK (or `requests` if Bob requires custom endpoint)

**Rationale**:
- **Official**: Maintained by Anthropic
- **Structured Output**: Supports JSON mode for parsing
- **Error Handling**: Built-in retry logic
- **Cost Tracking**: Token usage tracking
- **Simplicity**: No framework overhead (vs langchain)

**Fallback**: If Bob API uses custom endpoint, use `requests` with Bob's format

**Trade-offs**:
- Anthropic-specific (not portable to OpenAI)
- Requires API key management
- No local LLM fallback

**Impact**: Reliable LLM integration, critical for content generation

---

## Decision 10: Modular Component Design

**Context**: Need to build 7 pages + 5 core modules in 45 hours.

**Options Considered**:
1. Monolithic app.py with all logic
2. Modular design with single-responsibility modules
3. Object-oriented class hierarchy

**Decision**: Modular design with functional modules

**Rationale**:
- **Parallel Development**: Can build modules independently
- **Testing**: Each module testable in isolation
- **Bob Efficiency**: Can generate entire modules in single prompts
- **Maintainability**: Clear separation of concerns
- **Reusability**: Modules can be used across pages

**Module Structure**:
- `db_inspector.py` - Database introspection only
- `llm_generator.py` - LLM orchestration only
- `session_manager.py` - State management only
- `query_executor.py` - Query execution only
- `markdown_exporter.py` - Document generation only

**Trade-offs**:
- More files to manage
- Import overhead
- Potential circular dependencies (avoided by design)

**Impact**: Enables efficient Bob code generation, critical for Bobcoin budget

---

## Decision 11: SQL Server System Tables for Introspection

**Context**: Need to extract schema metadata (tables, columns, relationships).

**Options Considered**:
1. `INFORMATION_SCHEMA` views (ANSI standard)
2. `sys.*` catalog views (SQL Server specific)
3. Hybrid approach (both)

**Decision**: Hybrid approach - `INFORMATION_SCHEMA` + `sys.*`

**Rationale**:
- **INFORMATION_SCHEMA**: Portable, covers basic metadata (tables, columns)
- **sys.***: Required for foreign keys, indexes, extended properties
- **Completeness**: Need both for full schema understanding
- **Performance**: Both are system views (fast)

**Queries**:
- Tables/Columns: `INFORMATION_SCHEMA.TABLES`, `INFORMATION_SCHEMA.COLUMNS`
- Foreign Keys: `sys.foreign_keys`, `sys.foreign_key_columns`
- Indexes: `sys.indexes`, `sys.index_columns`

**Trade-offs**:
- SQL Server specific (not portable to PostgreSQL, MySQL)
- More complex queries
- Requires understanding of both systems

**Impact**: Provides complete schema metadata for LLM generation

---

## Decision 12: Force-Directed Layout for Schema Map

**Context**: Need to visualize 70 tables with relationships in readable format.

**Options Considered**:
1. Hierarchical layout (tree structure)
2. Circular layout (nodes in circle)
3. Force-directed layout (physics simulation)
4. Manual positioning (user-defined)

**Decision**: Force-directed layout with physics enabled

**Rationale**:
- **Automatic**: No manual positioning needed
- **Relationship Emphasis**: Connected nodes cluster together
- **Scalability**: Handles 70 nodes without overlap
- **Interactivity**: Users can drag nodes to explore
- **Visual Appeal**: Organic, visually interesting

**Configuration**:
- Physics: Enabled (nodes repel, edges attract)
- Directed: True (arrows show FK direction)
- Node size: Based on table importance (row count or FK count)
- Node color: Based on functional grouping (LLM-generated)

**Trade-offs**:
- Non-deterministic (layout changes each render)
- Can be chaotic for highly connected graphs
- Requires user interaction to explore

**Impact**: Creates distinctive visual feature for hackathon demo

---

## Summary of Key Decisions

| Decision | Impact on Timeline | Impact on Budget | Risk Level |
|----------|-------------------|------------------|------------|
| Streamlit multi-page | -15 hours saved | 0 coins | Low |
| pyodbc | -5 hours saved | 0 coins | Low |
| streamlit-agraph | +3 hours risk | +2 coins risk | Medium |
| Bob API batch | -10 hours saved | +5 coins cost | Low |
| Three-tier strategy | -8 hours saved | 0 coins | Low |
| Session state | -3 hours saved | 0 coins | Low |
| Read-only queries | +2 hours cost | +1 coin cost | Low |
| Markdown export | -5 hours saved | 0 coins | Low |
| Anthropic SDK | -2 hours saved | 0 coins | Low |
| Modular design | -10 hours saved | -5 coins saved | Low |
| Hybrid SQL queries | +1 hour cost | 0 coins | Low |
| Force-directed layout | +2 hours cost | +2 coins cost | Medium |

**Net Impact**: -50 hours saved, +5 coins cost, 2 medium-risk decisions

**Conclusion**: Architecture optimized for hackathon constraints (time, budget, solo developer)

---

## Lessons for Bob Session Report

1. **Modular Design Enables AI Efficiency**: Single-responsibility modules allow Bob to generate complete, working components in single prompts (saves Bobcoins)

2. **Early Deployment Reduces Risk**: Three-tier strategy with Tier 1 deployment catches platform issues early (saves time)

3. **Batch LLM Calls Optimize Cost**: Generating all content during introspection cheaper than per-page generation (saves Bobcoins)

4. **Leverage Platform Strengths**: Using Streamlit's native features (multi-page, session state) faster than custom solutions (saves time)

5. **Fallback Plans Mitigate Risk**: streamlit-agraph with graphviz fallback ensures Schema Map works even if primary choice fails (reduces risk)

These decisions demonstrate strategic thinking under constraints - the core skill for hackathon success.