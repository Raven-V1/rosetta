"""
LLM Generator Module
Handles LLM-powered content generation using IBM watsonx.ai.
Uses ibm/granite-4-h-small model via REST API.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "ibm/granite-4-h-small"
WATSONX_URL = "https://us-south.ml.cloud.ibm.com"

_cached_iam_token = None


def _get_iam_token() -> str:
    global _cached_iam_token
    _cached_iam_token = None  # Always get fresh token

    api_key = os.getenv("WATSONX_API_KEY")
    if not api_key:
        raise ValueError("WATSONX_API_KEY environment variable is not set.")

    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }

    try:
        response = requests.post(token_url, headers=headers, data=data)
        logger.info(f"IAM token response status: {response.status_code}")
        logger.info(f"IAM token response: {response.text[:300]}")
        response.raise_for_status()
        _cached_iam_token = response.json()["access_token"]
        logger.info("Successfully obtained IAM token")
        return _cached_iam_token
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error getting token: {e.response.status_code} {e.response.text[:300]}")
        if e.response.status_code == 400:
            raise ValueError(f"IAM 400 error: {e.response.text[:300]}") from e
        elif e.response.status_code == 401:
            raise ValueError("Unauthorized: IBM Cloud API key authentication failed.") from e
        else:
            raise ValueError(f"IBM Cloud IAM authentication failed: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Failed to obtain IAM token: {str(e)}") from e


def _generate_text(prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
    project_id = os.getenv("WATSONX_PROJECT_ID")
    if not project_id:
        raise ValueError("WATSONX_PROJECT_ID environment variable is not set.")

    token = _get_iam_token()

    url = f"{WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "model_id": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "top_k": 50
        },
        "project_id": project_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Generation response status: {response.status_code}")
        logger.info(f"Generation response: {response.text[:300]}")
        response.raise_for_status()
        result = response.json()
        return result["results"][0]["generated_text"]
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error in generation: {e.response.status_code} {e.response.text[:300]}")
        if e.response.status_code == 401:
            global _cached_iam_token
            _cached_iam_token = None
            raise ValueError("Unauthorized: watsonx.ai authentication failed.") from e
        elif e.response.status_code == 403:
            raise ValueError("Forbidden: Access denied to watsonx.ai.") from e
        elif e.response.status_code == 404:
            raise ValueError("Not found: Invalid project ID or model.") from e
        else:
            raise ValueError(f"watsonx.ai API call failed: {str(e)}") from e
    except KeyError as e:
        raise ValueError(f"Unexpected response format from watsonx.ai: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"watsonx.ai API call failed: {str(e)}") from e


def generate_overview(metadata: Dict) -> str:
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

        prompt = f"""You are analyzing a SQL Server database for onboarding documentation.

Database: {database_name}
Tables: {table_count}
Relationships: {relationship_count}

Sample tables by schema:
{chr(10).join(schema_summary)}

Write a concise 2-3 sentence overview paragraph that:
1. Identifies the likely business domain/purpose of this database
2. Describes the main functional areas based on table names
3. Mentions the scale (number of tables and relationships)

Be specific and professional."""

        overview = _generate_text(prompt=prompt, max_tokens=2000, temperature=0.7)
        return overview.strip()

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during overview generation: {e}")
        return _get_fallback_overview(metadata)


def generate_table_descriptions(tables: List[Dict]) -> Dict[str, str]:
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

        prompt = f"""Generate a concise one-sentence description for each table below.

Tables:
{chr(10).join(table_list)}

Return a JSON object where keys are full table names and values are descriptions.
Example: {{"dbo.Users": "Stores user account credentials and profile information"}}"""

        response_text = _generate_text(prompt=prompt, max_tokens=3000, temperature=0.7).strip()

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                json_lines.append(line)
            response_text = '\n'.join(json_lines)

        return json.loads(response_text)

    except json.JSONDecodeError:
        return _get_fallback_descriptions(tables)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table descriptions: {e}")
        return _get_fallback_descriptions(tables)


def generate_tier1_content(metadata: Dict) -> Dict:
    logger.info("Starting Tier 1 content generation")
    overview = generate_overview(metadata)
    tables = metadata.get('tables', [])
    table_descriptions = generate_table_descriptions(tables)
    return {
        'overview': overview,
        'table_descriptions': table_descriptions
    }


def generate_sample_queries(metadata: Dict) -> List[Dict]:
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
            rel_summary.append(f"- {rel.get('from_table', '')} -> {rel.get('to_table', '')}")

        prompt = f"""Generate 10-15 sample SQL queries for database onboarding.

Database: {database_name}

Tables:
{chr(10).join(table_list)}

Relationships:
{chr(10).join(rel_summary) if rel_summary else "None provided"}

Include SELECT, JOIN, aggregation, and filtering queries.

Return a JSON array:
[{{"title": "...", "annotation": "...", "sql": "..."}}]"""

        response_text = _generate_text(prompt=prompt, max_tokens=2000, temperature=0.7).strip()

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                json_lines.append(line)
            response_text = '\n'.join(json_lines)

        return json.loads(response_text)

    except json.JSONDecodeError:
        return _get_fallback_queries(metadata)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during sample queries: {e}")
        return _get_fallback_queries(metadata)


def rank_important_tables(metadata: Dict) -> List[Dict]:
    try:
        database_name = metadata.get('database_name', 'Unknown')
        tables = metadata.get('tables', [])
        relationships = metadata.get('relationships', [])

        connection_counts = {}
        for rel in relationships:
            from_table = rel.get('from_table', '')
            to_table = rel.get('to_table', '')
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

        prompt = f"""Identify the top 5 most important tables for database onboarding.

Database: {database_name}

Tables sorted by relationships:
{chr(10).join(table_list)}

Return a JSON array of exactly 5 objects:
[{{"table": "schema.name", "description": "...", "reasoning": "...", "connections": 0}}]"""

        response_text = _generate_text(prompt=prompt, max_tokens=1500, temperature=0.7).strip()

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                json_lines.append(line)
            response_text = '\n'.join(json_lines)

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
    database_name = metadata.get('database_name', 'Unknown Database')
    table_count = len(metadata.get('tables', []))
    relationship_count = len(metadata.get('relationships', []))
    return (f"{database_name} is a SQL Server database containing {table_count} tables "
            f"with {relationship_count} foreign key relationships.")


def _get_fallback_descriptions(tables: List[Dict]) -> Dict[str, str]:
    descriptions = {}
    for table in tables:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        descriptions[full_name] = f"Stores {name.lower()} data and related information"
    return descriptions


def _get_fallback_queries(metadata: Dict) -> List[Dict]:
    tables = metadata.get('tables', [])
    queries = []
    for table in tables[:3]:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        queries.append({
            'title': f"Select All from {name}",
            'annotation': f"Retrieves all records from the {name} table.",
            'sql': f"SELECT TOP 100 * FROM {full_name};"
        })
    return queries


def _get_fallback_rankings(metadata: Dict) -> List[Dict]:
    tables = metadata.get('tables', [])
    relationships = metadata.get('relationships', [])
    connection_counts = {}
    for rel in relationships:
        from_table = rel.get('from_table', '')
        to_table = rel.get('to_table', '')
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