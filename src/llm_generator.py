"""
LLM Generator Module
Handles LLM-powered content generation using IBM watsonx.ai.

Tier 1 Responsibilities:
- Generate database overview summary
- Generate table descriptions

Uses ibm/granite-4-h-small model for efficient content generation.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_ID = "ibm/granite-4-h-small"
WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

# Module-level token cache
_cached_iam_token = None


def _get_iam_token() -> str:
    """
    Obtain and cache IAM Bearer token for watsonx.ai authentication.
    
    Returns:
        str: Bearer token for API authentication
        
    Raises:
        Exception: If authentication fails
    """
    global _cached_iam_token
    
    # Return cached token if available
    if _cached_iam_token:
        return _cached_iam_token
    
    # Check if API key is configured
    if not WATSONX_API_KEY:
        error_msg = "WATSONX_API_KEY environment variable is not set. Please configure your IBM Cloud API key."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Obtain new token
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WATSONX_API_KEY
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        _cached_iam_token = token_data["access_token"]
        logger.info("Successfully obtained IAM token")
        return _cached_iam_token
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_msg = "Invalid IBM Cloud API key. Please check your WATSONX_API_KEY environment variable."
        elif e.response.status_code == 401:
            error_msg = "Unauthorized: IBM Cloud API key authentication failed. Please verify your credentials."
        else:
            error_msg = f"IBM Cloud IAM authentication failed with status {e.response.status_code}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"Failed to obtain IAM token: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def _generate_text(prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
    """
    Generate text using watsonx.ai REST API.
    
    Args:
        prompt: Input prompt for text generation
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        
    Returns:
        str: Generated text response
        
    Raises:
        Exception: If API call fails
    """
    # Check if project ID is configured
    if not WATSONX_PROJECT_ID:
        error_msg = "WATSONX_PROJECT_ID environment variable is not set. Please configure your IBM watsonx project ID."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    token = _get_iam_token()
    
    url = f"{WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "model_id": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "top_k": 50
        },
        "project_id": WATSONX_PROJECT_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        generated_text = result["results"][0]["generated_text"]
        return generated_text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            error_msg = "Unauthorized: watsonx.ai authentication failed. Your IAM token may have expired or is invalid."
        elif e.response.status_code == 403:
            error_msg = "Forbidden: Access denied to watsonx.ai. Please check your project ID and permissions."
        elif e.response.status_code == 404:
            error_msg = "Not found: Invalid watsonx.ai project ID or model. Please verify WATSONX_PROJECT_ID."
        else:
            error_msg = f"watsonx.ai API call failed with status {e.response.status_code}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except KeyError as e:
        error_msg = f"Unexpected response format from watsonx.ai: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"watsonx.ai API call failed: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def generate_overview(metadata: Dict) -> str:
    """
    Generate a high-level database overview paragraph.
    
    Args:
        metadata: Database metadata dict from db_inspector.get_database_metadata()
        
    Returns:
        str: Overview paragraph describing the database purpose and structure
        
    Raises:
        ValueError: If authentication or API configuration fails
        
    Example:
        >>> metadata = get_database_metadata(conn_string)
        >>> overview = generate_overview(metadata)
        >>> print(overview)
        "AdventureWorks2025 is a comprehensive database..."
    """
    try:
        # Prepare metadata summary for the prompt
        table_count = len(metadata.get('tables', []))
        relationship_count = len(metadata.get('relationships', []))
        database_name = metadata.get('database_name', 'Unknown')
        
        # Get table names grouped by schema
        tables_by_schema = {}
        for table in metadata.get('tables', []):
            schema = table.get('schema', 'dbo')
            if schema not in tables_by_schema:
                tables_by_schema[schema] = []
            tables_by_schema[schema].append(table.get('name', ''))
        
        # Build schema summary
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

Be specific and professional. Do not use generic phrases like "appears to be" - be confident in your analysis based on the table names."""

        logger.info(f"Generating overview for {database_name}")
        
        overview = _generate_text(prompt=prompt, max_tokens=2000, temperature=0.7)
        
        logger.info("Overview generation successful")
        return overview.strip()
        
    except ValueError as e:
        # Re-raise authentication and configuration errors
        logger.error(f"Configuration/Authentication error in overview generation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during overview generation: {e}")
        logger.warning("Falling back to basic overview")
        return _get_fallback_overview(metadata)


def generate_table_descriptions(tables: List[Dict]) -> Dict[str, str]:
    """
    Generate concise descriptions for each table based on name and columns.
    
    Args:
        tables: List of table dicts with 'schema', 'name', and 'columns' keys
        
    Returns:
        dict: Mapping of 'schema.table' to description string
        
    Raises:
        ValueError: If authentication or API configuration fails
        
    Example:
        >>> tables = metadata['tables']
        >>> descriptions = generate_table_descriptions(tables)
        >>> descriptions['dbo.Users']
        "Stores user account information including credentials and profile data"
    """
    try:
        # Prepare table information for the prompt
        table_info = []
        for table in tables:
            schema = table.get('schema', 'dbo')
            name = table.get('name', '')
            columns = table.get('columns', [])
            column_names = [col.get('name', '') for col in columns[:10]]  # First 10 columns
            
            table_info.append({
                'full_name': f"{schema}.{name}",
                'name': name,
                'columns': column_names
            })
        
        # Limit to first 50 tables if database is large
        if len(table_info) > 50:
            logger.warning(f"Large database detected ({len(table_info)} tables). Limiting to top 50.")
            table_info = table_info[:50]
        
        # Build the prompt
        table_list = []
        for t in table_info:
            cols = ', '.join(t['columns'][:5]) + (' ...' if len(t['columns']) > 5 else '')
            table_list.append(f"- {t['full_name']}: columns [{cols}]")
        
        prompt = f"""You are analyzing SQL Server database tables for onboarding documentation.

Generate a concise one-sentence description for each table below. Each description should:
1. Explain what data the table stores
2. Be 10-15 words maximum
3. Use present tense ("Stores...", "Contains...", "Tracks...")
4. Be specific based on table name and column names

Tables to describe:
{chr(10).join(table_list)}

Return your response as a JSON object where keys are the full table names (schema.table) and values are the descriptions.

Example format:
{{
  "dbo.Users": "Stores user account credentials and profile information",
  "dbo.Orders": "Contains customer purchase orders and transaction details"
}}"""

        logger.info(f"Generating descriptions for {len(table_info)} tables")
        
        response_text = _generate_text(prompt=prompt, max_tokens=3000, temperature=0.7).strip()
        
        # Parse JSON response
        # Handle potential markdown code blocks
        if response_text.startswith('```'):
            # Extract JSON from code block
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                if in_block or (not line.startswith('```')):
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        descriptions = json.loads(response_text)
        
        logger.info(f"Successfully generated {len(descriptions)} table descriptions")
        return descriptions
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in table descriptions: {e}")
        logger.warning("Falling back to basic table descriptions")
        return _get_fallback_descriptions(tables)
    except ValueError as e:
        # Re-raise authentication and configuration errors
        logger.error(f"Configuration/Authentication error in table descriptions: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table description generation: {e}")
        logger.warning("Falling back to basic table descriptions")
        return _get_fallback_descriptions(tables)


def generate_tier1_content(metadata: Dict) -> Dict:
    """
    Generate all Tier 1 content in an efficient batch.
    Calls overview first, then descriptions.
    Caches results to avoid duplicate API calls.
    
    Args:
        metadata: Database metadata dict from db_inspector.get_database_metadata()
        
    Returns:
        dict: Contains 'overview' and 'table_descriptions' keys
        
    Example:
        >>> metadata = get_database_metadata(conn_string)
        >>> content = generate_tier1_content(metadata)
        >>> print(content['overview'])
        >>> print(content['table_descriptions']['dbo.Users'])
    """
    logger.info("Starting Tier 1 content generation")
    
    # Generate overview
    overview = generate_overview(metadata)
    
    # Generate table descriptions
    tables = metadata.get('tables', [])
    table_descriptions = generate_table_descriptions(tables)
    
    result = {
        'overview': overview,
        'table_descriptions': table_descriptions
    }
    
    logger.info("Tier 1 content generation complete")
    return result


def _get_fallback_overview(metadata: Dict) -> str:
    """
    Generate a basic fallback overview when API fails.
    
    Args:
        metadata: Database metadata dict
        
    Returns:
        str: Fallback overview text
    """
    database_name = metadata.get('database_name', 'Unknown Database')
    table_count = len(metadata.get('tables', []))
    relationship_count = len(metadata.get('relationships', []))
    
    return (f"{database_name} is a SQL Server database containing {table_count} tables "
            f"with {relationship_count} foreign key relationships. This database appears to "
            f"support business operations across multiple functional areas based on its schema structure.")


def _get_fallback_descriptions(tables: List[Dict]) -> Dict[str, str]:
    """
    Generate basic fallback descriptions when API fails.
    
    Args:
        tables: List of table dicts
        
    Returns:
        dict: Mapping of table names to basic descriptions
    """
    descriptions = {}
    for table in tables:
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        
        # Generate simple description based on table name
        descriptions[full_name] = f"Stores {name.lower()} data and related information"
    
    return descriptions


# Module-level constants
TIER1_FUNCTIONS = ['generate_overview', 'generate_table_descriptions']

# Made with Bob


def generate_sample_queries(metadata: Dict) -> List[Dict]:
    """
    Generate 10-15 sample SQL queries demonstrating common database patterns.
    
    Args:
        metadata: Database metadata dict from db_inspector.get_database_metadata()
        
    Returns:
        list: List of query dicts, each containing:
            - title: str - Descriptive title for the query
            - annotation: str - Explanation of what the query does and why it's useful
            - sql: str - The actual SQL query
            
    Raises:
        ValueError: If authentication or API configuration fails
            
    Example:
        >>> metadata = get_database_metadata(conn_string)
        >>> queries = generate_sample_queries(metadata)
        >>> print(queries[0]['title'])
        >>> print(queries[0]['sql'])
    """
    try:
        # Prepare metadata summary for the prompt
        database_name = metadata.get('database_name', 'Unknown')
        tables = metadata.get('tables', [])
        relationships = metadata.get('relationships', [])
        
        # Get sample table information
        table_info = []
        for table in tables[:20]:  # Limit to first 20 tables
            schema = table.get('schema', 'dbo')
            name = table.get('name', '')
            columns = table.get('columns', [])
            column_names = [col.get('name', '') for col in columns[:8]]
            
            table_info.append({
                'full_name': f"{schema}.{name}",
                'columns': column_names
            })
        
        # Build table list for prompt
        table_list = []
        for t in table_info:
            cols = ', '.join(t['columns'])
            table_list.append(f"- {t['full_name']}: [{cols}]")
        
        # Build relationship summary
        rel_summary = []
        for rel in relationships[:10]:  # First 10 relationships
            rel_summary.append(f"- {rel.get('from_table', '')} -> {rel.get('to_table', '')}")
        
        prompt = f"""You are creating sample SQL queries for database onboarding documentation.

Database: {database_name}

Sample Tables:
{chr(10).join(table_list)}

Sample Relationships:
{chr(10).join(rel_summary) if rel_summary else "No relationships provided"}

Generate 10-15 sample SQL queries that demonstrate common patterns in this database. Include a variety of:
- Simple SELECT queries with filtering
- JOIN queries (INNER, LEFT, etc.)
- Aggregation queries (COUNT, SUM, AVG, GROUP BY)
- Sorting and limiting results
- Subqueries or CTEs where appropriate
- Queries that showcase the database's business logic

For each query, provide:
1. A descriptive title (5-8 words)
2. An annotation explaining what the query does and why it's useful (1-2 sentences)
3. The actual SQL query (properly formatted)

Return your response as a JSON array of objects with this structure:
[
  {{
    "title": "Get All Active Users",
    "annotation": "Retrieves all users with active status. Useful for understanding current user base.",
    "sql": "SELECT * FROM dbo.Users WHERE Status = 'Active';"
  }}
]

Make the queries realistic and useful for someone learning this database."""

        logger.info(f"Generating sample queries for {database_name}")
        
        response_text = _generate_text(prompt=prompt, max_tokens=2000, temperature=0.7).strip()
        
        # Parse JSON response
        # Handle potential markdown code blocks
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                if in_block or (not line.startswith('```')):
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        queries = json.loads(response_text)
        
        logger.info(f"Successfully generated {len(queries)} sample queries")
        return queries
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in sample queries: {e}")
        logger.warning("Falling back to basic sample queries")
        return _get_fallback_queries(metadata)
    except ValueError as e:
        # Re-raise authentication and configuration errors
        logger.error(f"Configuration/Authentication error in sample queries: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during sample query generation: {e}")
        logger.warning("Falling back to basic sample queries")
        return _get_fallback_queries(metadata)


def rank_important_tables(metadata: Dict) -> List[Dict]:
    """
    Identify and rank the top 5 most important tables in the database.
    
    Args:
        metadata: Database metadata dict from db_inspector.get_database_metadata()
        
    Returns:
        list: List of 5 table dicts, each containing:
            - table: str - Table name in schema.table format
            - description: str - What the table represents
            - reasoning: str - Why this table is important
            - connections: int - Number of relationships this table has
            
    Raises:
        ValueError: If authentication or API configuration fails
        
    Example:
        >>> metadata = get_database_metadata(conn_string)
        >>> important_tables = rank_important_tables(metadata)
        >>> print(important_tables[0]['table'])
        >>> print(important_tables[0]['reasoning'])
    """
    try:
        # Prepare metadata for analysis
        database_name = metadata.get('database_name', 'Unknown')
        tables = metadata.get('tables', [])
        relationships = metadata.get('relationships', [])
        
        # Calculate connection counts for each table
        connection_counts = {}
        for rel in relationships:
            from_table = rel.get('from_table', '')
            to_table = rel.get('to_table', '')
            connection_counts[from_table] = connection_counts.get(from_table, 0) + 1
            connection_counts[to_table] = connection_counts.get(to_table, 0) + 1
        
        # Build table information with connection counts
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
        
        # Sort by connections and row count for better context
        table_info.sort(key=lambda x: (x['connections'], x['row_count']), reverse=True)
        
        # Build table list for prompt (top 30 by connections)
        table_list = []
        for t in table_info[:30]:
            cols = ', '.join(t['columns'][:5]) + (' ...' if len(t['columns']) > 5 else '')
            table_list.append(
                f"- {t['full_name']}: {t['connections']} relationships, "
                f"{t['row_count']} rows, columns [{cols}]"
            )
        
        prompt = f"""You are analyzing a SQL Server database to identify the most important tables for onboarding documentation.

Database: {database_name}

Tables (sorted by relationship count):
{chr(10).join(table_list)}

Analyze the tables and identify the TOP 5 most important tables. Consider:
1. Number of relationships (highly connected tables are often central)
2. Table names that suggest core business entities
3. Row counts (larger tables often contain key data)
4. Column names that indicate primary business data

For each of the top 5 tables, provide:
1. The table name (schema.table format)
2. A brief description of what the table represents (1 sentence)
3. Reasoning for why this table is important (1-2 sentences)
4. The number of relationships/connections

Return your response as a JSON array of exactly 5 objects with this structure:
[
  {{
    "table": "dbo.Users",
    "description": "Stores user account and authentication information",
    "reasoning": "Central to the system as most other tables reference users for tracking and permissions. High relationship count indicates it's a core entity.",
    "connections": 15
  }}
]

Rank them from most important (1st) to 5th most important."""

        logger.info(f"Ranking important tables for {database_name}")
        
        response_text = _generate_text(prompt=prompt, max_tokens=1500, temperature=0.7).strip()
        
        # Parse JSON response
        # Handle potential markdown code blocks
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith('```'):
                    in_block = not in_block
                    continue
                if in_block or (not line.startswith('```')):
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        ranked_tables = json.loads(response_text)
        
        # Ensure we have exactly 5 tables
        if len(ranked_tables) > 5:
            ranked_tables = ranked_tables[:5]
        
        logger.info(f"Successfully ranked {len(ranked_tables)} important tables")
        return ranked_tables
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in table rankings: {e}")
        logger.warning("Falling back to basic table rankings")
        return _get_fallback_rankings(metadata)
    except ValueError as e:
        # Re-raise authentication and configuration errors to be handled by the UI
        logger.error(f"Configuration/Authentication error in table ranking: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table ranking: {e}")
        logger.warning("Falling back to basic table rankings")
        return _get_fallback_rankings(metadata)


def _get_fallback_queries(metadata: Dict) -> List[Dict]:
    """
    Generate basic fallback sample queries when API fails.
    
    Args:
        metadata: Database metadata dict
        
    Returns:
        list: List of basic sample query dicts
    """
    tables = metadata.get('tables', [])
    queries = []
    
    # Generate simple queries for first few tables
    for i, table in enumerate(tables[:3]):
        schema = table.get('schema', 'dbo')
        name = table.get('name', '')
        full_name = f"{schema}.{name}"
        
        queries.append({
            'title': f"Select All from {name}",
            'annotation': f"Retrieves all records from the {name} table. Useful for exploring table contents.",
            'sql': f"SELECT TOP 100 * FROM {full_name};"
        })
    
    return queries


def _get_fallback_rankings(metadata: Dict) -> List[Dict]:
    """
    Generate basic fallback table rankings when API fails.
    
    Args:
        metadata: Database metadata dict
        
    Returns:
        list: List of basic ranked table dicts
    """
    tables = metadata.get('tables', [])
    relationships = metadata.get('relationships', [])
    
    # Calculate connection counts
    connection_counts = {}
    for rel in relationships:
        from_table = rel.get('from_table', '')
        to_table = rel.get('to_table', '')
        connection_counts[from_table] = connection_counts.get(from_table, 0) + 1
        connection_counts[to_table] = connection_counts.get(to_table, 0) + 1
    
    # Sort tables by connection count
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
    
    # Sort by connections and return top 5
    ranked.sort(key=lambda x: x['connections'], reverse=True)
    return ranked[:5]


# Module-level constants
TIER2_FUNCTIONS = ['generate_sample_queries', 'rank_important_tables']
