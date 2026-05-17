"""
LLM Generator Module
Handles LLM-powered content generation using Groq API.
Uses llama-3.1-8b-instant model via REST API.
"""

import os
import re
import json
import logging
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_ID = "llama-3.1-8b-instant"


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response, tolerating preamble text and code fences."""
    text = text.strip()
    block = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if block:
        return block.group(1).strip()
    for start, end in [('[', ']'), ('{', '}')]:
        s = text.find(start)
        e = text.rfind(end)
        if s != -1 and e > s:
            return text[s:e + 1]
    return text


def _generate_text(prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    """
    Generate text using Groq API.
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation (0.0-1.0)
        
    Returns:
        Generated text response
        
    Raises:
        ValueError: If GROQ_API_KEY is not configured or API call fails
    """
    # Read API key fresh for each call
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("LLM features require GROQ_API_KEY to be configured")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        logger.info(f"Groq API response status: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error in generation: {e.response.status_code} {e.response.text[:300]}")
        if e.response.status_code == 401:
            raise ValueError("Unauthorized: Invalid GROQ_API_KEY") from e
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded. Please try again later.") from e
        else:
            raise ValueError(f"Groq API call failed: {str(e)}") from e
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. Please try again.") from None
    except KeyError as e:
        raise ValueError(f"Unexpected response format from Groq API: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Groq API call failed: {str(e)}") from e


def generate_overview(metadata: Dict) -> str:
    """
    Generate a database overview using LLM.
    
    Args:
        metadata: Database metadata dictionary
        
    Returns:
        Overview text describing the database
    """
    try:
        table_count = len(metadata.get('tables', []))
        relationship_count = len(metadata.get('relationships', []))
        database_name = metadata.get('database_name', 'Unknown')

        tables_by_schema = {}
        for table in metadata.get('tables', []):
            schema = table.get('schema', 'dbo')
            if schema not in tables_by_schema:
                tables_by_schema[schema] = []
            tables_by_schema[schema].append(table.get('name', ''))

        schema_summary = []
        for schema, tables in tables_by_schema.items():
            schema_summary.append(f"- {schema}: {', '.join(tables[:5])}" +
                                (" ..." if len(tables) > 5 else ""))

        prompt = f"""You are writing onboarding documentation for a new developer joining a team.

Database: {database_name}
Tables: {table_count}
Relationships: {relationship_count}

Tables by schema:
{chr(10).join(schema_summary)}

Write a rich 4-5 sentence overview paragraph for the onboarding guide that:
1. Identifies the business domain and purpose of this database
2. Describes the main functional areas (e.g. customers, orders, inventory, HR)
3. Explains how the main areas connect to each other
4. Mentions the scale and any notable characteristics
5. Recommends where a new developer should start exploring

Write in clear, professional English. Be specific — name actual table groups, not generic descriptions."""

        overview = _generate_text(prompt=prompt, max_tokens=1500, temperature=0.3)
        return overview.strip()

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during overview generation: {e}")
        return _get_fallback_overview(metadata)


def generate_table_descriptions(tables: List[Dict]) -> Dict[str, str]:
    """
    Generate descriptions for database tables using LLM.
    
    Args:
        tables: List of table metadata dictionaries
        
    Returns:
        Dictionary mapping table names to descriptions
    """
    try:
        table_info = []
        for table in tables:
            schema = table.get('schema', 'dbo')
            name = table.get('name', '')
            columns = table.get('columns', [])
            column_names = [col.get('name', '') for col in columns[:10]]
            table_info.append({
                'full_name': f"{schema}.{name}",
                'columns': column_names
            })

        if len(table_info) > 50:
            table_info = table_info[:50]

        table_list = []
        for t in table_info:
            cols = ', '.join(t['columns'][:5]) + (' ...' if len(t['columns']) > 5 else '')
            table_list.append(f"- {t['full_name']}: columns [{cols}]")

        prompt = f"""You are writing a database glossary for a new developer joining a team.
For each table below, write a 2-sentence description:
- Sentence 1: what this table stores and its business purpose
- Sentence 2: key relationships, typical usage patterns, or what a developer should know first

Tables:
{chr(10).join(table_list)}

Return a JSON object where keys are full table names (schema.table) and values are the 2-sentence descriptions.
Example: {{"dbo.Orders": "Stores customer purchase orders including status, totals, and shipping details. It is the central transaction table — most reporting queries start here and join to order_items, customers, and payments."}}

Return only valid JSON, no other text."""

        response_text = _extract_json(_generate_text(prompt=prompt, max_tokens=3500, temperature=0.3))
        return json.loads(response_text)

    except json.JSONDecodeError:
        return _get_fallback_descriptions(tables)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table descriptions: {e}")
        return _get_fallback_descriptions(tables)


def generate_tier1_content(metadata: Dict) -> Dict:
    """
    Generate Tier 1 content (overview and table descriptions).
    
    Args:
        metadata: Database metadata dictionary
        
    Returns:
        Dictionary with 'overview' and 'table_descriptions' keys
    """
    logger.info("Starting Tier 1 content generation")
    overview = generate_overview(metadata)
    tables = metadata.get('tables', [])
    table_descriptions = generate_table_descriptions(tables)
    return {
        'overview': overview,
        'table_descriptions': table_descriptions
    }


def generate_sample_queries(metadata: Dict) -> List[Dict]:
    """
    Generate sample SQL queries for the database.
    
    Args:
        metadata: Database metadata dictionary
        
    Returns:
        List of query dictionaries with 'title', 'annotation', and 'sql' keys
    """
    try:
        database_name = metadata.get('database_name', 'Unknown')
        tables = metadata.get('tables', [])
        relationships = metadata.get('relationships', [])

        table_info = []
        for table in tables[:20]:
            schema = table.get('schema', 'dbo')
            name = table.get('name', '')
            columns = table.get('columns', [])
            column_names = [col.get('name', '') for col in columns[:8]]
            table_info.append({
                'full_name': f"{schema}.{name}",
                'columns': column_names
            })

        table_list = []
        for t in table_info:
            cols = ', '.join(t['columns'])
            table_list.append(f"- {t['full_name']}: [{cols}]")

        rel_summary = []
        for rel in relationships[:10]:
            rel_summary.append(f"- {rel.get('parent_table', '')} -> {rel.get('referenced_table', '')}")

        prompt = f"""You are writing onboarding sample queries for a new developer joining a team.
Generate 12-15 SQL queries that help someone understand and navigate this database.

Database: {database_name}

Tables (with columns):
{chr(10).join(table_list)}

Foreign key relationships:
{chr(10).join(rel_summary) if rel_summary else "No relationships provided"}

Requirements:
- Cover a mix of: simple lookups, JOINs across related tables, aggregations (COUNT, SUM, AVG), status/date filtering
- Avoid trivial SELECT * queries — prefer queries that answer a real business question
- Each annotation must explain WHAT business question this query answers, not just what SQL it runs
- Use correct table and column names from the lists above

Return a JSON array only, no other text:
[{{"title": "Short descriptive title", "annotation": "What business question this answers and when you would run it", "sql": "SELECT ..."}}]"""

        response_text = _extract_json(_generate_text(prompt=prompt, max_tokens=2500, temperature=0.3))
        return json.loads(response_text)

    except json.JSONDecodeError:
        return _get_fallback_queries(metadata)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during sample queries: {e}")
        return _get_fallback_queries(metadata)


def rank_important_tables(metadata: Dict) -> List[Dict]:
    """
    Rank and identify the most important tables in the database.
    
    Args:
        metadata: Database metadata dictionary
        
    Returns:
        List of top 5 important tables with descriptions and reasoning
    """
    try:
        database_name = metadata.get('database_name', 'Unknown')
        tables = metadata.get('tables', [])
        relationships = metadata.get('relationships', [])

        connection_counts = {}
        for rel in relationships:
            from_table = rel.get('parent_table', '')
            to_table = rel.get('referenced_table', '')
            connection_counts[from_table] = connection_counts.get(from_table, 0) + 1
            connection_counts[to_table] = connection_counts.get(to_table, 0) + 1

        table_info = []
        for table in tables:
            schema = table.get('schema', 'dbo')
            name = table.get('name', '')
            full_name = f"{schema}.{name}"
            columns = table.get('columns', [])
            column_names = [col.get('name', '') for col in columns[:10]]
            connections = connection_counts.get(full_name, 0)
            table_info.append({
                'full_name': full_name,
                'columns': column_names,
                'connections': connections,
                'row_count': table.get('row_count', 0)
            })

        table_info.sort(key=lambda x: (x['connections'], x['row_count']), reverse=True)

        table_list = []
        for t in table_info[:30]:
            cols = ', '.join(t['columns'][:5]) + (' ...' if len(t['columns']) > 5 else '')
            table_list.append(
                f"- {t['full_name']}: {t['connections']} relationships, "
                f"{t['row_count']} rows, columns [{cols}]"
            )

        prompt = f"""You are writing a "Start Here" guide for a new developer joining a team.
Identify the 5 most important tables a new developer should understand first.

Database: {database_name}

Tables sorted by number of relationships (most connected first):
{chr(10).join(table_list)}

For each table, write:
- description: 1 clear sentence on what this table stores
- reasoning: 2-3 sentences explaining WHY this table matters for onboarding — what business process it drives, what other tables depend on it, and what a developer should look at first
- connections: integer count of relationships

Return a JSON array of exactly 5 objects, no other text:
[{{"table": "schema.name", "description": "...", "reasoning": "...", "connections": 0}}]"""

        response_text = _extract_json(_generate_text(prompt=prompt, max_tokens=1500, temperature=0.3))
        ranked_tables = json.loads(response_text)
        return ranked_tables[:5]

    except json.JSONDecodeError:
        return _get_fallback_rankings(metadata)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table ranking: {e}")
        return _get_fallback_rankings(metadata)


def _get_fallback_overview(metadata: Dict) -> str:
    """Generate a basic fallback overview when LLM is unavailable."""
    database_name = metadata.get('database_name', 'Unknown Database')
    table_count = len(metadata.get('tables', []))
    relationship_count = len(metadata.get('relationships', []))
    return (f"{database_name} is a SQL Server database containing {table_count} tables "
            f"with {relationship_count} foreign key relationships.")


def _get_fallback_descriptions(tables: List[Dict]) -> Dict[str, str]:
    """Generate basic fallback descriptions when LLM is unavailable."""
    descriptions = {}
    for table in tables:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        descriptions[full_name] = f"Stores {name.lower()} data and related information"
    return descriptions


def _get_fallback_queries(metadata: Dict) -> List[Dict]:
    """Generate basic fallback queries when LLM is unavailable."""
    tables = metadata.get('tables', [])
    queries = []
    for table in tables[:3]:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        queries.append({
            'title': f"Preview {name}",
            'annotation': f"Returns the first 100 rows of {name}. Use this to inspect the table structure and sample data.",
            'sql': f"SELECT TOP 100 * FROM {full_name};"
        })
    return queries


def _get_fallback_rankings(metadata: Dict) -> List[Dict]:
    """Generate basic fallback rankings when LLM is unavailable."""
    tables = metadata.get('tables', [])
    relationships = metadata.get('relationships', [])
    connection_counts = {}
    for rel in relationships:
        from_table = rel.get('parent_table', '')
        to_table = rel.get('referenced_table', '')
        connection_counts[from_table] = connection_counts.get(from_table, 0) + 1
        connection_counts[to_table] = connection_counts.get(to_table, 0) + 1
    ranked = []
    for table in tables:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        connections = connection_counts.get(full_name, 0)
        ranked.append({
            'table': full_name,
            'description': f"Table storing {name.lower()} data",
            'reasoning': f"Has {connections} relationships with other tables",
            'connections': connections
        })
    ranked.sort(key=lambda x: x['connections'], reverse=True)
    return ranked[:5]


# Made with Bob