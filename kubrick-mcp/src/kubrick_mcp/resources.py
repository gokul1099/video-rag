from typing import Dict
from kubrick_mcp.video.ingestion.models import CachedTable, CachedTableMetadata
from kubrick_mcp.video.ingestion.registry import get_registry
from fastmcp.resources import resource

def list_tables() -> Dict[str, str]:
    """
    List all video indexes currently available
    """

    keys= list(get_registry().keys())
    if not keys:
        return None
    
    response = {
        "messages": "Current processed video",
        "indexes": keys
    }
    return response


def table_info(table_name: str) -> str:
    """
    List information about a specific video index
    """
    registry= get_registry()
    if table_name not in registry:
        return f"Video index '{table_name}' does not exists"
    table_metadata = registry[table_name]
    table_info = CachedTableMetadata(**table_metadata)
    table = CachedTable.from_metadata(table_info)
    response = table.describe()
    return response