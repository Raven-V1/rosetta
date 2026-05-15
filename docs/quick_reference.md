# Rosetta Quick Reference Guide
**Fast lookup for implementation decisions**

---

## Critical Constraints

| Constraint | Value |
|------------|-------|
| Time Remaining | 45 hours |
| Bobcoin Budget | 37 remaining (target: 35 spent) |
| Database | AdventureWorks2025 (SQL Server 2025) |
| Deployment | Streamlit Community Cloud (free) |
| License | MIT |
| Repository | github.com/Raven-V1/rosetta |

---

## Tech Stack

| Component | Library | Version | Rationale |
|-----------|---------|---------|-----------|
| Framework | Streamlit | 1.31.0 | Multi-page native, free hosting |
| Database | pyodbc | 5.0.1 | ODBC Driver 17 on Streamlit Cloud |
| LLM | anthropic | 0.18.1 | Bob/Claude API integration |
| Graph | streamlit-agraph | 0.0.45 | Interactive, Streamlit-native |
| Fallback Graph | graphviz | 0.20.1 | If streamlit-agraph fails |
| Data | pandas | 2.1.4 | Native Streamlit integration |

---

## Implementation Order

### Tier 1: Core (20h, 10 coins)
1. Project setup (1h)
2. `db_inspector.py` (3h, 2 coins)
3. `llm_generator.py` basic (3h, 3 coins)
4. `session_manager.py` (1h)
5. Page 1: Home (2h, 1 coin)
6. Page 2: Overview (2h)
7. Page 6: Glossary (3h, 1 coin)
8. Page 7: Download (2h)
9. Deploy (3h, 3 coins)

### Tier 2: Interactive (15h, 15 coins)
1. `llm_generator.py` full (4h, 5 coins)
2. `query_executor.py` (3h, 2 coins)
3. Page 4: Start Here (2h, 1 coin)
4. Page 5: First Queries (4h, 3 coins)
5. Page 3: Schema Map (6h, 4 coins)
6. Enhanced Glossary (2h)

### Tier 3: Polish (10h, 10 coins)
1. Error handling (3h, 2 coins)
2. Loading states (2h, 1 coin)
3. UI polish (2h, 1 coin)
4. Performance (2h, 2 coins)
5. Demo materials (4h)
6. Testing (3h, 3 coins)

---

## Module Responsibilities

| Module | Single Responsibility | Key Functions |
|--------|----------------------|---------------|
| `db_inspector.py` | Database introspection | `validate_connection()`, `get_database_metadata()` |
| `llm_generator.py` | LLM content generation | `generate_overview()`, `rank_important_tables()` |
| `session_manager.py` | State management | `store_metadata()`, `get_metadata()` |
| `query_executor.py` | Safe query execution | `execute_query()`, `validate_query()` |
| `markdown_exporter.py` | Document assembly | `export_to_markdown()` |

---

## Page Flow

```
1. Home → Enter connection string → Introspect (60s) → Store in session
2. Overview → Read session → Display summary
3. Schema Map → Read session → Render graph
4. Start Here → Read session → Show ranked tables
5. First Queries → Read session → Execute on click
6. Glossary → Read session → Searchable list
7. Download → Read session → Export Markdown
```

---

## LLM API Calls (4-5 coins per introspection)

| Call | Purpose | Input | Output | Cost |
|------|---------|-------|--------|------|
| 1 | Overview | Full metadata | Summary paragraph | 1 coin |
| 2 | Descriptions | Table list | Dict of descriptions | 1-2 coins |
| 3 | Rankings | Full metadata | Top 3-5 tables with reasoning | 1 coin |
| 4 | Queries | Full metadata | 10-15 annotated queries | 1 coin |

---

## Session State Schema

```python
st.session_state = {
    'connected': bool,
    'conn_string': str,
    'metadata': {
        'database_name': str,
        'server': str,
        'tables': [
            {
                'schema': str,
                'name': str,
                'row_count': int,
                'columns': [
                    {'name': str, 'type': str, 'nullable': bool}
                ]
            }
        ],
        'relationships': [
            {
                'fk_name': str,
                'parent_table': str,
                'parent_column': str,
                'referenced_table': str,
                'referenced_column': str
            }
        ]
    },
    'generated': {
        'overview': str,
        'table_descriptions': {'table_name': 'description'},
        'table_groups': {'group_name': ['table1', 'table2']},
        'important_tables': [
            {
                'table': str,
                'description': str,
                'reasoning': str,
                'connections': [str]
            }
        ],
        'sample_queries': [
            {
                'title': str,
                'annotation': str,
                'sql': str
            }
        ]
    },
    'introspection_time': float
}
```

---

## SQL Queries for Introspection

### Tables
```sql
SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
```

### Columns
```sql
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, 
       CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
```

### Foreign Keys
```sql
SELECT 
    fk.name AS FK_NAME,
    tp.name AS PARENT_TABLE,
    cp.name AS PARENT_COLUMN,
    tr.name AS REFERENCED_TABLE,
    cr.name AS REFERENCED_COLUMN
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id 
    AND fkc.parent_object_id = cp.object_id
INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id 
    AND fkc.referenced_object_id = cr.object_id
```

---

## Security Rules

### Query Validation
**Reject**: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`, `TRUNCATE`  
**Allow**: `SELECT`, `WITH` (CTEs), `EXPLAIN`  
**Limits**: 30s timeout, 1000 rows max

### Connection String
- Never log connection strings
- Use password input field (masked)
- Clear from session on disconnect

---

## Deployment Checklist

### Pre-Deploy
- [ ] All dependencies in `requirements.txt`
- [ ] No hardcoded secrets
- [ ] `.gitignore` configured
- [ ] Python 3.11 specified

### Streamlit Cloud
- [ ] Repo connected
- [ ] Main branch selected
- [ ] `app.py` as entry point
- [ ] Secrets configured (optional)

### Post-Deploy
- [ ] Test public URL
- [ ] Verify all pages load
- [ ] Test connection
- [ ] Check logs

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ODBC driver not found | Use `Driver={ODBC Driver 17 for SQL Server}` |
| streamlit-agraph fails | Fallback to graphviz |
| LLM timeout | Implement retry with exponential backoff |
| Session state lost | Expected on refresh, re-introspect |
| Query timeout | 30s limit, show partial results |
| Large database (>100 tables) | Limit to top 50 by row count |

---

## File Naming Conventions

### Pages
Format: `{number}_{emoji}_{Name}.py`  
Example: `1_🏠_Home.py`

### Modules
Format: `{purpose}_{type}.py`  
Example: `db_inspector.py`

### Tests
Format: `test_{module}.py`  
Example: `test_db_inspector.py`

---

## Git Commit Messages

Format: `{type}: {description}`

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructure
- `test:` - Tests
- `deploy:` - Deployment config

Examples:
- `feat: implement database inspector module`
- `fix: handle connection timeout errors`
- `docs: update README with usage instructions`

---

## Bobcoin Tracking

| Phase | Budget | Actual | Remaining |
|-------|--------|--------|-----------|
| Start | 37 | 0 | 37 |
| Tier 1 | 10 | TBD | TBD |
| Tier 2 | 15 | TBD | TBD |
| Tier 3 | 10 | TBD | TBD |
| Target | 35 | TBD | 2 buffer |

---

## Testing Checklist

### Functional
- [ ] Connect to AdventureWorks2025
- [ ] All 70 tables appear
- [ ] Schema Map renders
- [ ] Queries execute
- [ ] Markdown exports

### Edge Cases
- [ ] Invalid connection string
- [ ] Empty database
- [ ] Database with 1000+ tables
- [ ] Query timeout
- [ ] Connection loss

### Performance
- [ ] Introspection <60s
- [ ] Page navigation <1s
- [ ] Query execution <30s
- [ ] Graph rendering <5s

---

## Demo Materials Checklist

- [ ] Demo video (2-3 minutes)
- [ ] Pitch deck (5-10 slides)
- [ ] Screenshots for README
- [ ] Bob session report export
- [ ] GitHub repo public
- [ ] README complete

---

## Emergency Fallbacks

| Feature | Primary | Fallback |
|---------|---------|----------|
| Graph | streamlit-agraph | graphviz SVG |
| LLM | Bob API | Pre-generated templates |
| Database | SQL Server | SQLite sample |
| Deployment | Streamlit Cloud | Local demo |

---

## Key Metrics for Success

| Metric | Target | Stretch |
|--------|--------|---------|
| Introspection time | <60s | <30s |
| Page load time | <1s | <500ms |
| Query execution | <30s | <10s |
| Bobcoins spent | 35 | 30 |
| Time to Tier 1 | 20h | 15h |
| Total time | 45h | 40h |

---

## Contact & Resources

- **Repository**: github.com/Raven-V1/rosetta
- **Deployment**: Streamlit Community Cloud
- **Database**: AdventureWorks2025 (local SQL Server 2025)
- **LLM**: Bob/Claude API
- **License**: MIT

---

## Quick Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Run tests
pytest tests/
```

### Git Workflow
```bash
# Initial setup
git init
git add .
git commit -m "feat: initial project setup"
git remote add origin https://github.com/Raven-V1/rosetta.git
git push -u origin main

# Feature development
git checkout -b feature/db-inspector
git add src/db_inspector.py
git commit -m "feat: implement database inspector"
git push origin feature/db-inspector
```

### Deployment
```bash
# Push to main (triggers Streamlit Cloud deploy)
git checkout main
git merge develop
git push origin main
```

---

This quick reference should be your go-to guide during implementation. Keep it open for fast lookups!