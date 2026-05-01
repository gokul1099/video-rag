from contextlib import asynccontextmanager
from fastmcp.client import Client
from kubrick_api.config import get_settings
from loguru import logger

class MCPClientSingleTon:
    """Singleton for MCP client to reuse connections"""

    _instance = None
    _client = None
    def __init__(self):
        self.settings = get_settings()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_cleint(self) -> Client:
        """Get or create MCP client"""
        if self._client is None:
            self._client = Client(self.settings.MCP_SERVER)
        return self._client
    
    async def call_tool(self,tool_name: str, params: dict):
        """Call MCP tools with connection management"""
        client = await self.get_cleint()
        async with client:
            result = await client.call_tool(tool_name, params)
            return result
    
    async def close(self):
        """Close the client connection"""
        if self._client:
            await self._client.close()
            self._client = None

mcp_client = MCPClientSingleTon()