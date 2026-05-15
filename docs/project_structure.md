# Rosetta Project Structure
**Recommended file and folder organization for implementation**

---

## Directory Tree

```
rosetta/
├── .gitignore
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── README.md
├── LICENSE                          # MIT License
├── requirements.txt                 # Python dependencies
├── plan.md                          # Implementation plan (this planning session)
├── decisions.md                     # Architectural decisions
├── project_structure.md             # This file
│
├── app.py                           # Main entry point (minimal, redirects to Home)
│
├── src/                             # Core business logic modules
│   ├── __init__.py
│   ├── db_inspector.py              # Database schema introspection
│   ├── llm_generator.py             # LLM content generation
│   ├── session_manager.py           # Streamlit session state management
│   ├── query_executor.py            # Safe query execution
│   └── markdown_exporter.py         # Documentation export
│
├── pages/                           # Streamlit multi-page app pages
│   ├── 1_🏠_Home.py                 # Connection page
│   ├── 2_📊_Overview.py             # Database summary
│   ├── 3_🗺️_Schema_Map.py          # Interactive diagram
│   ├── 4_🎯_Start_Here.py           # Ranked important tables
│   ├── 5_💻_First_Queries.py        # Sample queries with execution
│   ├── 6_📖_Glossary.py             # Searchable table list
│   └── 7_⬇️_Download.py             # Markdown export
│
├── tests/                           # Unit tests (optional, if time permits)
│   ├── __init__.py
│   ├── test_db_inspector.py
│   ├── test_query_executor.py
│   └── test_session_manager.py
│
└── assets/                          # Demo materials
    ├── demo.mp4                     # Demo video
    ├── pitch.pdf                    # Pitch deck
    └── screenshots/                 # Screenshots for README
        ├── home.png
        ├── overview.png
        ├── schema_map.png
        └── queries.png
```

---

## File Purposes

### Root Level Files

#### `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Local database files
*.db
*.sqlite
```

#### `README.md`
Should include:
- Project description
- Installation instructions
- Usage guide
- Demo link
- Screenshots
- License

#### `LICENSE`
MIT License text

#### `requirements.txt`
See detailed breakdown below

---

### Configuration Files

#### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false
```

---

### Core Modules (`src/`)

#### `src/__init__.py`
```python
"""
Rosetta - Database Onboarding Generator
Core business logic modules
"""

__version__ = "1.0.0"
```

#### `src/db_inspector.py`
**Purpose**: Database schema introspection  
**Responsibilities**:
- Validate SQL Server connections
- Extract table metadata
- Extract column metadata
- Extract foreign key relationships
- Extract index information
- Get row counts
- Get sample data

**Key Functions**:
- `validate_connection(conn_string: str) -> bool`
- `get_database_metadata(conn_string: str) -> dict`
- `get_table_row_counts(conn_string: str, tables: list) -> dict`
- `get_sample_data(conn_string: str, table: str, limit: int) -> pd.DataFrame`

**Dependencies**: `pyodbc`, `pandas`

---

#### `src/llm_generator.py`
**Purpose**: LLM-powered content generation  
**Responsibilities**:
- Generate database overview
- Generate table descriptions
- Generate functional groupings
- Rank important tables
- Generate sample queries

**Key Functions**:
- `generate_overview(metadata: dict) -> str`
- `generate_table_descriptions(tables: list) -> dict[str, str]`
- `generate_table_groupings(metadata: dict) -> dict[str, list]`
- `rank_important_tables(metadata: dict) -> list[dict]`
- `generate_sample_queries(metadata: dict) -> list[dict]`

**Dependencies**: `anthropic` (or `requests` for Bob API)

---

#### `src/session_manager.py`
**Purpose**: Streamlit session state management  
**Responsibilities**:
- Initialize session state
- Store/retrieve metadata
- Store/retrieve generated content
- Check connection status
- Clear session

**Key Functions**:
- `initialize_session() -> None`
- `store_metadata(metadata: dict) -> None`
- `get_metadata() -> dict`
- `store_generated_content(content: dict) -> None`
- `get_generated_content() -> dict`
- `is_connected() -> bool`
- `clear_session() -> None`

**Dependencies**: `streamlit`

---

#### `src/query_executor.py`
**Purpose**: Safe query execution  
**Responsibilities**:
- Validate queries (read-only)
- Execute queries with timeout
- Format results
- Handle errors

**Key Functions**:
- `execute_query(conn_string: str, query: str, params: dict = None) -> pd.DataFrame`
- `validate_query(query: str) -> bool`
- `execute_with_timeout(conn_string: str, query: str, timeout: int = 30) -> pd.DataFrame`

**Dependencies**: `pyodbc`, `pandas`

---

#### `src/markdown_exporter.py`
**Purpose**: Documentation export  
**Responsibilities**:
- Assemble all sections
- Format Markdown
- Generate downloadable file

**Key Functions**:
- `export_to_markdown(session_data: dict) -> str`
- `format_table_section(table: dict) -> str`
- `format_query_section(query: dict) -> str`

**Dependencies**: None (pure Python)

---

### Pages (`pages/`)

#### `pages/1_🏠_Home.py`
**Purpose**: Landing page with connection form  
**UI Elements**:
- Hero section
- Connection string input
- Connect button
- Status messages

**Session State Usage**:
- Writes: `conn_string`, `connected`, `metadata`, `generated`
- Reads: `connected`

---

#### `pages/2_📊_Overview.py`
**Purpose**: Database summary  
**UI Elements**:
- Database info
- Key metrics
- LLM-generated overview

**Session State Usage**:
- Reads: `metadata`, `generated['overview']`

---

#### `pages/3_🗺️_Schema_Map.py`
**Purpose**: Interactive diagram  
**UI Elements**:
- streamlit-agraph graph
- Legend
- Zoom/pan controls

**Session State Usage**:
- Reads: `metadata['relationships']`, `generated['table_groups']`

---

#### `pages/4_🎯_Start_Here.py`
**Purpose**: Ranked important tables  
**UI Elements**:
- Numbered list
- Table descriptions
- Reasoning
- Connections

**Session State Usage**:
- Reads: `generated['important_tables']`

---

#### `pages/5_💻_First_Queries.py`
**Purpose**: Sample queries with execution  
**UI Elements**:
- Query list
- Run buttons
- Results tables
- Download CSV

**Session State Usage**:
- Reads: `conn_string`, `generated['sample_queries']`

---

#### `pages/6_📖_Glossary.py`
**Purpose**: Searchable table list  
**UI Elements**:
- Search box
- Table list
- Expandable details

**Session State Usage**:
- Reads: `metadata['tables']`, `generated['table_descriptions']`

---

#### `pages/7_⬇️_Download.py`
**Purpose**: Markdown export  
**UI Elements**:
- Preview
- Download button

**Session State Usage**:
- Reads: All session state

---

## Dependencies (`requirements.txt`)

```txt
# Core Framework
streamlit==1.31.0

# Database
pyodbc==5.0.1

# Data Processing
pandas==2.1.4

# LLM Integration
anthropic==0.18.1

# Graph Visualization
streamlit-agraph==0.0.45

# Fallback Visualization (if streamlit-agraph fails)
graphviz==0.20.1

# Utilities
python-dotenv==1.0.0  # For local .env file (optional)
```

**Total Size**: ~50MB (acceptable for Streamlit Cloud)

---

## Development Workflow

### Phase 1: Setup (1 hour)
1. Create directory structure
2. Initialize Git repository
3. Create `requirements.txt`
4. Create `.gitignore`
5. Create `README.md` skeleton
6. Push to GitHub

### Phase 2: Core Modules (10 hours)
1. Implement `db_inspector.py` (3 hours)
2. Implement `llm_generator.py` (3 hours)
3. Implement `session_manager.py` (1 hour)
4. Implement `query_executor.py` (2 hours)
5. Implement `markdown_exporter.py` (1 hour)

### Phase 3: Tier 1 Pages (9 hours)
1. Create `app.py` (1 hour)
2. Implement Page 1: Home (2 hours)
3. Implement Page 2: Overview (2 hours)
4. Implement Page 6: Glossary (2 hours)
5. Implement Page 7: Download (2 hours)

### Phase 4: Deployment (3 hours)
1. Test locally with AdventureWorks
2. Push to GitHub
3. Deploy to Streamlit Cloud
4. Debug deployment issues

### Phase 5: Tier 2 Pages (12 hours)
1. Implement Page 4: Start Here (2 hours)
2. Implement Page 5: First Queries (4 hours)
3. Implement Page 3: Schema Map (6 hours)

### Phase 6: Polish (10 hours)
1. Error handling (3 hours)
2. UI improvements (2 hours)
3. Performance optimization (2 hours)
4. Testing (3 hours)

---

## Git Workflow

### Branch Strategy
- `main` - Production (deployed to Streamlit Cloud)
- `develop` - Integration branch
- `feature/*` - Feature branches (optional for solo dev)

### Commit Strategy
- Commit after each module completion
- Commit after each page completion
- Commit before deployment
- Use descriptive commit messages

### Example Commits
```
feat: implement database inspector module
feat: add LLM content generation
feat: create Home page with connection form
fix: handle connection timeout errors
docs: update README with usage instructions
deploy: configure Streamlit Cloud settings
```

---

## Testing Strategy

### Unit Tests (Optional)
If time permits, create tests for:
- `db_inspector.py` - Mock database connections
- `query_executor.py` - Validate query validation logic
- `session_manager.py` - Test state management

### Manual Testing Checklist
- [ ] Connect to AdventureWorks2025
- [ ] Verify all 70 tables appear
- [ ] Check Schema Map renders
- [ ] Execute sample queries
- [ ] Export Markdown
- [ ] Test on Streamlit Cloud
- [ ] Test with invalid connection string
- [ ] Test with empty database
- [ ] Test query timeout
- [ ] Test large result sets

---

## Deployment Checklist

### Pre-Deployment
- [ ] All dependencies in `requirements.txt`
- [ ] No hardcoded secrets
- [ ] `.gitignore` configured
- [ ] README complete
- [ ] License file present

### Streamlit Cloud Setup
- [ ] GitHub repo connected
- [ ] Python version set to 3.11
- [ ] Secrets configured (if needed)
- [ ] Custom domain (optional)

### Post-Deployment
- [ ] Test public URL
- [ ] Verify all pages load
- [ ] Test with demo connection string
- [ ] Check logs for errors
- [ ] Monitor resource usage

---

## File Size Estimates

| Component | Lines of Code | Estimated Size |
|-----------|---------------|----------------|
| `db_inspector.py` | 200-300 | 8-12 KB |
| `llm_generator.py` | 150-250 | 6-10 KB |
| `session_manager.py` | 50-100 | 2-4 KB |
| `query_executor.py` | 100-150 | 4-6 KB |
| `markdown_exporter.py` | 100-150 | 4-6 KB |
| Each page | 100-200 | 4-8 KB |
| Total Python code | ~1500 | ~60 KB |

**Total Project Size**: <100 KB (excluding dependencies)

---

## Next Steps

1. **Review this structure** - Confirm organization makes sense
2. **Create directories** - Set up folder structure
3. **Initialize Git** - Create repository
4. **Start with core modules** - Build foundation first
5. **Implement pages** - Build UI on top of modules

This structure supports:
- ✅ Modular development
- ✅ Parallel implementation
- ✅ Easy testing
- ✅ Clear separation of concerns
- ✅ Streamlit best practices