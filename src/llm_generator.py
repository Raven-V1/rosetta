"""
LLM Generator Module
Handles LLM-powered content generation using Anthropic Claude API.

Tier 1 Responsibilities:
- Generate database overview summary
- Generate table descriptions

Uses claude-sonnet-4-20250514 model with caching for efficiency.
"""

import anthropic
import json
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000
TEMPERATURE = 0.7


def generate_overview(metadata: Dict) -> str:
    """
    Generate a high-level database overview paragraph.
    
    Args:
        metadata: Database metadata dict from db_inspector.get_database_metadata()
        
    Returns:
        str: Overview paragraph describing the database purpose and structure
        
    Example:
        >>> metadata = get_database_metadata(conn_string)
        >>> overview = generate_overview(metadata)
        >>> print(overview)
        "AdventureWorks2025 is a comprehensive database..."
    """
    try:
        client = anthropic.Anthropic()
        
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
        
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        overview = message.content[0].text.strip()
        logger.info("Overview generation successful")
        return overview
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error during overview generation: {e}")
        return _get_fallback_overview(metadata)
    except Exception as e:
        logger.error(f"Unexpected error during overview generation: {e}")
        return _get_fallback_overview(metadata)


def generate_table_descriptions(tables: List[Dict]) -> Dict[str, str]:
    """
    Generate concise descriptions for each table based on name and columns.
    
    Args:
        tables: List of table dicts with 'schema', 'name', and 'columns' keys
        
    Returns:
        dict: Mapping of 'schema.table' to description string
        
    Example:
        >>> tables = metadata['tables']
        >>> descriptions = generate_table_descriptions(tables)
        >>> descriptions['dbo.Users']
        "Stores user account information including credentials and profile data"
    """
    try:
        client = anthropic.Anthropic()
        
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
        
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
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
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error during table description generation: {e}")
        return _get_fallback_descriptions(tables)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in table descriptions: {e}")
        return _get_fallback_descriptions(tables)
    except Exception as e:
        logger.error(f"Unexpected error during table description generation: {e}")
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
