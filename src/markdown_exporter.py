"""
Markdown Exporter Module
Handles export of onboarding documentation to Markdown format.

Responsibilities:
- Assemble full onboarding document from session state
- Format database overview section
- Format table glossary with descriptions and columns
- Format sample queries with annotations
- Format schema summary with relationships

Pure Python only. No external dependencies.
"""

from typing import Dict, List, Optional


def export_to_markdown(session_data: dict) -> str:
    """
    Assemble full onboarding document from session state.
    
    Creates a comprehensive Markdown document with sections:
    - Database Overview
    - Table Glossary
    - Sample Queries
    - Schema Summary
    
    Args:
        session_data: Full st.session_state dict containing:
            - metadata: Database metadata (tables, relationships, etc.)
            - generated: LLM-generated content (overview, descriptions, queries)
            - conn_string: Connection string (optional, for reference)
            
    Returns:
        str: Complete Markdown document ready for download
        
    Example:
        >>> markdown = export_to_markdown(st.session_state)
        >>> st.download_button("Download", markdown, "onboarding.md")
    """
    # Extract data from session state
    metadata = session_data.get('metadata', {})
    generated = session_data.get('generated', {})
    
    # Build document sections
    sections = []
    
    # Title and header
    database_name = metadata.get('database_name', 'Unknown Database')
    server = metadata.get('server', 'Unknown Server')
    sections.append(f"# {database_name} - Database Onboarding Guide")
    sections.append("")
    sections.append(f"**Server**: {server}")
    sections.append(f"**Generated**: {_get_timestamp()}")
    sections.append("")
    sections.append("---")
    sections.append("")
    
    # Database Overview section
    sections.append("## 📊 Database Overview")
    sections.append("")
    overview = generated.get('overview', '')
    if overview:
        sections.append(overview)
    else:
        sections.append("*No overview available*")
    sections.append("")
    
    # Key metrics
    table_count = len(metadata.get('tables', []))
    relationship_count = len(metadata.get('relationships', []))
    sections.append("### Key Metrics")
    sections.append("")
    sections.append(f"- **Total Tables**: {table_count}")
    sections.append(f"- **Foreign Key Relationships**: {relationship_count}")
    sections.append("")
    sections.append("---")
    sections.append("")
    
    # Important Tables section (if available)
    important_tables = generated.get('important_tables', [])
    if important_tables:
        sections.append("## 🎯 Start Here - Important Tables")
        sections.append("")
        sections.append("These tables are recommended starting points for understanding the database:")
        sections.append("")
        for i, table_info in enumerate(important_tables, 1):
            sections.append(f"### {i}. {table_info.get('table', 'Unknown Table')}")
            sections.append("")
            sections.append(f"**Why it matters**: {table_info.get('reasoning', 'No reasoning provided')}")
            sections.append("")
            
            # Add description if available
            table_descriptions = generated.get('table_descriptions', {})
            table_name = table_info.get('table', '')
            if table_name in table_descriptions:
                sections.append(f"**Description**: {table_descriptions[table_name]}")
                sections.append("")
            
            # Add connections if available
            connections = table_info.get('connections', [])
            if connections:
                if isinstance(connections, list):
                    sections.append(f"**Connected to**: {', '.join(str(c) for c in connections)}")
                elif isinstance(connections, (int, float)) and connections > 0:
                    sections.append(f"**Connections**: {int(connections)} relationships")
                sections.append("")
        
        sections.append("---")
        sections.append("")
    
    # Sample Queries section
    sample_queries = generated.get('sample_queries', [])
    if sample_queries:
        sections.append("## 💻 Sample Queries")
        sections.append("")
        sections.append("These queries demonstrate common patterns and use cases:")
        sections.append("")
        
        for i, query in enumerate(sample_queries, 1):
            query_section = format_query_section(query, i)
            sections.append(query_section)
            sections.append("")
        
        sections.append("---")
        sections.append("")
    
    # Table Glossary section
    tables = metadata.get('tables', [])
    table_descriptions = generated.get('table_descriptions', {})
    
    if tables:
        sections.append("## 📖 Table Glossary")
        sections.append("")
        sections.append("Complete list of all tables with descriptions and column details:")
        sections.append("")
        
        # Group tables by schema
        tables_by_schema = {}
        for table in tables:
            schema = table.get('schema', 'dbo')
            if schema not in tables_by_schema:
                tables_by_schema[schema] = []
            tables_by_schema[schema].append(table)
        
        # Output tables grouped by schema
        for schema in sorted(tables_by_schema.keys()):
            sections.append(f"### Schema: {schema}")
            sections.append("")
            
            for table in sorted(tables_by_schema[schema], key=lambda t: t.get('name', '')):
                table_section = format_table_section(table, table_descriptions)
                sections.append(table_section)
                sections.append("")
        
        sections.append("---")
        sections.append("")
    
    # Schema Summary section
    relationships = metadata.get('relationships', [])
    if relationships:
        sections.append("## 🗺️ Schema Summary")
        sections.append("")
        sections.append("### Foreign Key Relationships")
        sections.append("")
        sections.append("| Parent Table | Column | Referenced Table | Column |")
        sections.append("|--------------|--------|------------------|--------|")
        
        for rel in relationships:
            parent = rel.get('parent_table', '')
            parent_col = rel.get('parent_column', '')
            referenced = rel.get('referenced_table', '')
            referenced_col = rel.get('referenced_column', '')
            sections.append(f"| {parent} | {parent_col} | {referenced} | {referenced_col} |")
        
        sections.append("")
        sections.append("---")
        sections.append("")
    
    # Footer
    sections.append("## 📝 Notes")
    sections.append("")
    sections.append("This document was automatically generated by Rosetta, a database onboarding tool.")
    sections.append("For questions or updates, please contact your database administrator.")
    sections.append("")
    
    # Join all sections
    return "\n".join(sections)


def format_table_section(table: dict, table_descriptions: Optional[dict] = None) -> str:
    """
    Format one table entry with name, description, and columns.
    
    Args:
        table: Table dict with 'schema', 'name', 'row_count', 'columns' keys
        table_descriptions: Optional dict mapping table names to descriptions
        
    Returns:
        str: Formatted Markdown section for the table
        
    Example:
        >>> table = {'schema': 'dbo', 'name': 'Users', 'row_count': 1000, 'columns': [...]}
        >>> descriptions = {'dbo.Users': 'Stores user account information'}
        >>> print(format_table_section(table, descriptions))
    """
    schema = table.get('schema', 'dbo')
    name = table.get('name', 'Unknown')
    row_count = table.get('row_count', 0)
    columns = table.get('columns', [])
    
    full_name = f"{schema}.{name}"
    
    lines = []
    
    # Table header
    lines.append(f"#### {full_name}")
    lines.append("")
    
    # Description (if available)
    if table_descriptions and full_name in table_descriptions:
        lines.append(f"**Description**: {table_descriptions[full_name]}")
        lines.append("")
    
    # Row count
    lines.append(f"**Row Count**: {row_count:,}")
    lines.append("")
    
    # Columns table
    if columns:
        lines.append("**Columns**:")
        lines.append("")
        lines.append("| Column Name | Data Type | Nullable |")
        lines.append("|-------------|-----------|----------|")
        
        for col in columns:
            col_name = col.get('name', '')
            col_type = col.get('type', '')
            nullable = 'Yes' if col.get('nullable', False) else 'No'
            lines.append(f"| {col_name} | {col_type} | {nullable} |")
        
        lines.append("")
    else:
        lines.append("*No column information available*")
        lines.append("")
    
    return "\n".join(lines)


def format_query_section(query: dict, number: Optional[int] = None) -> str:
    """
    Format one query with title, annotation, and SQL code block.
    
    Args:
        query: Query dict with 'title', 'description', 'sql' keys
        number: Optional query number for numbering
        
    Returns:
        str: Formatted Markdown section for the query
        
    Example:
        >>> query = {
        ...     'title': 'Get Active Users',
        ...     'description': 'Returns all users who logged in within the last 30 days',
        ...     'sql': 'SELECT * FROM Users WHERE LastLogin > DATEADD(day, -30, GETDATE())'
        ... }
        >>> print(format_query_section(query, 1))
    """
    title = query.get('title', 'Untitled Query')
    description = query.get('description', '')
    sql = query.get('sql', '')
    
    lines = []
    
    # Query header
    if number:
        lines.append(f"### {number}. {title}")
    else:
        lines.append(f"### {title}")
    lines.append("")
    
    # Description/annotation
    if description:
        lines.append(f"**Purpose**: {description}")
        lines.append("")
    
    # SQL code block
    if sql:
        lines.append("```sql")
        lines.append(sql.strip())
        lines.append("```")
    else:
        lines.append("*No SQL provided*")
    
    return "\n".join(lines)


def _get_timestamp() -> str:
    """
    Get current timestamp in readable format.
    
    Returns:
        str: Formatted timestamp
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Module-level constants
__all__ = [
    'export_to_markdown',
    'format_table_section',
    'format_query_section'
]

# Made with Bob