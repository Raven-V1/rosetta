# Rosetta — Session Handoff
Session date: 2026-05-16
Repo: https://github.com/Raven-V1/rosetta
Local path: C:\Users\carlo\Documents\03_DEV\repos\rosetta
Live URL: https://rosetta-xu8drsbqv2tuahq6uagskl.streamlit.app
Current HEAD: 69574ca (main, in sync with origin)

---

## What Was Done This Session

### 1. Sidebar branding (all pages)

Created src/ui_utils.py with render_sidebar_brand().
Replaces the three-line inline branding block on every page with a single import.
The logo is base64-encoded and embedded in HTML so it centers properly.
Company name renders at 1.3rem bold.

Applied to: pages/1_Home.py, 2_Spotlight.py, 3_Overview.py, 4_Schema_Map.py,
5_Recommended_Queries.py, 6_Glossary.py, 7_Download.py.

### 2. Download page crashes fixed

Local crash — ModuleNotFoundError: No module named 'reportlab'
Fix: installed reportlab locally. The import is now wrapped in try/except
with _reportlab_available flag so the page degrades gracefully on platforms
where reportlab is not installed instead of crashing on load.

Cloud crash — TypeError: This app has encountered an error
Root cause: markdown_exporter.py line 103 called ', '.join(connections)
where connections was an int (relationship count from LLM JSON), not a list.
Fix: isinstance guard — if list, join; if int > 0, show as "N relationships".

### 3. pyodbc bare import fixed (carry-over from previous session)

src/query_executor.py line 14 had a bare top-level import pyodbc.
On Streamlit Cloud (Linux), pyodbc is not installed (win32-only in requirements).
Fix: wrapped in try/except with _pyodbc_available flag.
execute_with_timeout() returns empty DataFrame immediately if pyodbc unavailable.

### 4. Schema Map self-loop edges removed

pages/4_Schema_Map.py — added parent_table != referenced_table filter when
building edges. Self-referential foreign keys (employees.manager_id -> employees,
departments.parent_id -> departments) were rendering as confusing arrow loops
on the nodes.

### 5. Fallback query annotation improved

src/llm_generator.py _get_fallback_queries():
"Select All from X / Retrieves all records" changed to
"Preview X / Returns the first 100 rows of X. Use this to inspect structure."

### 6. PDF generator rewritten

pages/7_Download.py generate_pdf() — near-complete rewrite.

Headers and footers:
Every page now has a header (Belvenar logo, "Belvenar Analytics", database name,
blue rule) and a footer (brand tagline, page number, gray rule).
Implemented via draw_page() canvas callback passed to doc.build().

Proper table rendering:
Markdown table blocks (| col | col | / |---|) are now detected and converted
to reportlab Table objects with dark header row, alternating row shading, and
a light grid. Previously they were rendered as raw pipe-character Paragraph text.

Page break control:
Every #### table entry (heading + description + row count + columns table) is
wrapped in KeepTogether. The entire entry moves to a new page rather than
splitting mid-entry. For the #### level this is done via a sec[] buffer that
flushes as KeepTogether when the next heading is encountered.

### 7. LLM prompts enriched

All four generation functions in src/llm_generator.py updated:

generate_overview: 4-5 sentences; covers domain, functional areas, cross-area
connections, scale, and recommended starting point. max_tokens 1000 -> 1500.

generate_table_descriptions: 2-sentence format per table (what it stores +
how it relates or usage pattern). max_tokens 1000 -> 3500.

generate_sample_queries: 12-15 queries focused on real business questions, not
trivial SELECT *. Annotations explain the business question, not just the SQL.
max_tokens 1000 -> 2500.

rank_important_tables: 2-3 sentence reasoning covering business process,
dependents, and first-look advice. max_tokens 1000 -> 1500.

Note: generated content is cached in session state. To see richer output from
the new prompts, reconnect to the database so generators run fresh.

### 8. README and CONTRIBUTORS

README.md rewritten to reflect current app state:
- Accurate feature table for all 7 pages
- Demo database schema breakdown
- Local setup instructions
- SQL Server connection guide (lpc: protocol table)
- Streamlit Cloud deployment steps
- Full project structure tree
- Dependencies table
- LLM integration section
- Credits section

CONTRIBUTORS.md created listing Carlos Velazquez, IBM Bob, and Claude Code
with roles and specific contributions.

---

## Current App State

| Feature | Status |
|---|---|
| Try Demo (SQLite, 37 tables) | Working on cloud and locally |
| SQL Server (local run, lpc: protocol) | Working |
| SQL Server (cloud URL) | Not possible — cloud cannot reach local machine |
| Groq LLM (Spotlight, Overview, Queries) | Working when GROQ_API_KEY set |
| Schema Map graph | Working; self-loops removed |
| Recommended Queries page (cloud) | Working — pyodbc crash fixed |
| Download page PDF | Working — headers/footers, table rendering, page break control |
| Sidebar branding | Centered logo + 1.3rem bold name on all 7 pages |

---

## Known Remaining Issues

None critical. Potential areas for future work:

1. LLM content is generated fresh each reconnect. Consider caching to disk
   (e.g., a JSON sidecar next to the connection) so results persist across sessions.

2. Schema Map with many tables (37+) can be dense. Adding a node count limit
   or cluster-by-schema layout would improve readability.

3. The Recommended Queries Run Query button only works with SQL Server
   (pyodbc). It silently returns empty results for SQLite demo connections
   because execute_with_timeout() uses pyodbc.connect() which does not handle
   sqlite:// URIs.

4. PDF export for very wide column tables (many columns) may produce
   narrow columns that are hard to read. Custom column width logic based
   on content type (Column Name wider, Nullable narrower) would help.

---

## Commit Log This Session

69574ca  Update README to reflect current app state
e98e729  Rewrite PDF generator and enrich LLM prompts
8ba976f  Fix Download crashes, TypeError on export, schema map self-loops, and sidebar branding

---

## Key File Locations

| File | Purpose |
|---|---|
| pages/1_Home.py | Connection logic, SQL Server at line ~394 |
| pages/4_Schema_Map.py | Graph + edge filter at line ~139 |
| pages/7_Download.py | generate_pdf() — headers, table rendering, KeepTogether |
| src/ui_utils.py | render_sidebar_brand() — called by all 7 pages |
| src/llm_generator.py | All four LLM prompts and fallbacks |
| src/markdown_exporter.py | connections type guard at line ~101 |
| src/query_executor.py | pyodbc guard at top; execute_with_timeout() |
| demo_data.db | 37-table SQLite demo (816 KB, committed to repo) |
| create_demo_db.py | Regenerates demo_data.db from scratch |
| STREAMLIT_SECRETS_SETUP.md | Guide for adding GROQ_API_KEY to Streamlit Cloud |

---

## Environment Notes

- Python: local Windows environment, requirements installed including reportlab
- GROQ_API_KEY: set in local .env (not committed); also must be set in
  Streamlit Cloud Secrets for the cloud deployment to have LLM features
- pyodbc: installed locally (Windows); excluded from cloud install via
  sys_platform == "win32" in requirements.txt
