# Rosetta

Onboarding tool for developers inheriting unfamiliar databases.

Rosetta connects to a relational database, inspects its schema, and generates an interactive onboarding experience. A new developer can understand table structure, relationships, and common query patterns within their first hour instead of spending their first week reverse-engineering the schema from code.

Built by Belvenar Analytics for the IBM Bob Hackathon, May 2026.

---

## Live Demo

**[https://rosetta-xu8drsbqv2tuahq6uagskl.streamlit.app](https://rosetta-xu8drsbqv2tuahq6uagskl.streamlit.app)**

Click "Try Demo" on the Home page to explore a built-in 37-table retail database without connecting to anything.

---

## What It Does

Rosetta has seven pages, each serving a distinct onboarding purpose.

| Page | Description |
|---|---|
| Home | Connect to a database (SQL Server or SQLite) or load the built-in demo |
| Spotlight | LLM-ranked top 5 tables with reasoning about why each matters |
| Overview | High-level metrics, schema breakdown, and LLM-generated summary |
| Schema Map | Interactive force-directed graph of tables and foreign key relationships |
| Recommended Queries | LLM-generated SQL queries with business-context annotations; executable in-browser |
| Glossary | Searchable table reference with descriptions, column types, and row counts |
| Download | Export the full onboarding guide as a PDF with headers, footers, and formatted tables |

---

## Demo Database

The built-in demo is a 37-table retail/e-commerce SQLite database committed to the repo as `demo_data.db`. It requires no external connection.

| Domain | Tables |
|---|---|
| Customers | customers, addresses, customer_segments, wishlist_items |
| Staff | employees, departments, roles, employee_roles |
| Catalog | products, product_variants, product_images, product_attributes, brands, categories, tags, product_tags, price_history |
| Inventory | inventory, inventory_transactions, warehouses, suppliers, supplier_products, purchase_orders, purchase_order_items |
| Orders | orders, order_items, order_status_history, coupons, payments, payment_methods |
| Shipping | shipments, shipment_events, carriers |
| Engagement | reviews, review_votes |
| System | audit_logs, notifications |

Total rows: 9,887. To regenerate the database from scratch, run `python create_demo_db.py`.

---

## Running Locally

**Requirements:** Python 3.10+, pip

```bash
git clone https://github.com/Raven-V1/rosetta.git
cd rosetta
pip install -r requirements.txt
```

Copy the example environment file and add your Groq API key:

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

Start the app:

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. LLM features (Spotlight, Overview summary, Recommended Queries) require a valid `GROQ_API_KEY`. The demo database and all navigation work without it.

---

## Connecting to SQL Server

Rosetta connects to SQL Server using ODBC Driver 17. On Windows, local connections use the shared-memory protocol for best performance — no TCP/IP configuration required.

Supported server values on the Home page:

| Input | Protocol used |
|---|---|
| `localhost` | `lpc:localhost` (shared memory) |
| `.` | `lpc:.` (shared memory) |
| `(local)` | `lpc:(local)` (shared memory) |
| `192.168.x.x` | Direct TCP/IP |
| `host\INSTANCE` | Named instance (TCP/IP) |

**Note:** The live Streamlit Cloud deployment cannot reach a database running on your local machine. SQL Server connections only work when running the app locally.

---

## Deploying to Streamlit Cloud

1. Fork this repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing to your fork. Set the main file to `app.py`.
3. In the app settings, open the **Secrets** section and add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

4. Save and the app restarts automatically.

For full instructions see [STREAMLIT_SECRETS_SETUP.md](STREAMLIT_SECRETS_SETUP.md).

**Get a Groq API key:** [https://console.groq.com/keys](https://console.groq.com/keys) (free tier available)

---

## Project Structure

```
rosetta/
  app.py                    Entry point; page config and redirect to Home
  create_demo_db.py         Script to regenerate demo_data.db from scratch
  demo_data.db              Built-in 37-table SQLite demo database (816 KB)
  requirements.txt          Python dependencies
  .env.example              Template for local environment variables
  STREAMLIT_SECRETS_SETUP.md  Guide for configuring Groq API key on Streamlit Cloud

  pages/
    1_Home.py               Database connection (SQL Server, SQLite, demo)
    2_Spotlight.py          LLM-ranked important tables
    3_Overview.py           Database metrics and LLM overview
    4_Schema_Map.py         Interactive relationship graph (streamlit-agraph)
    5_Recommended_Queries.py  LLM-generated queries with execution
    6_Glossary.py           Searchable table and column reference
    7_Download.py           PDF export with headers, footers, formatted tables

  src/
    db_inspector.py         Database introspection (SQL Server and SQLite)
    llm_generator.py        Groq API integration (llama-3.1-8b-instant)
    markdown_exporter.py    Assembles the full onboarding document from session state
    query_executor.py       Read-only query validation and execution
    session_manager.py      Streamlit session state management
    ui_utils.py             Shared sidebar branding helper

  assets/
    Belvenar_logo.png       Sidebar and PDF header logo
```

---

## Dependencies

| Package | Purpose |
|---|---|
| streamlit >= 1.40 | App framework |
| pyodbc 5.3.0 | SQL Server connectivity (Windows only) |
| pandas >= 2.2 | Query result DataFrames |
| streamlit-agraph 0.0.45 | Interactive graph on Schema Map |
| reportlab | PDF generation on the Download page |
| python-dotenv | Local .env loading |
| requests | Groq API calls |

---

## LLM Integration

All AI features use the Groq API with the `llama-3.1-8b-instant` model. The app makes four types of generation calls:

- **Overview** — 4-5 sentence database summary covering domain, functional areas, and where to start
- **Table descriptions** — 2-sentence entry per table covering purpose and key relationships
- **Recommended Queries** — 12-15 queries with business-context annotations explaining what each answers
- **Important Tables** — Top 5 tables with reasoning about business role and onboarding priority

If `GROQ_API_KEY` is not set, the app falls back to static descriptions and preview queries so all pages remain usable.

---

## License

MIT
