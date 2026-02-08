import click
from fastmcp import FastMCP
from kubrick_mcp.tools import process_video, get_video_clip_from_user_query
from kubrick_mcp.resources import list_tables, table_info
from kubrick_mcp.prompts import routing_system_prompt, tool_use_system_prompt,general_system_prompt



def add_mcp_tool(mcp:FastMCP):
    mcp.tool(title="process video")(process_video)
    mcp.tool(title="get video clip from user query")(get_video_clip_from_user_query)

def add_mcp_resource(mcp:FastMCP):
    mcp.resource("video://tables/list")(list_tables)
    mcp.resource("video://tables/{table_name}")(table_info)
    

def add_mcp_prompts(mcp:FastMCP):
    mcp.prompt()(tool_use_system_prompt)
    mcp.prompt()(general_system_prompt)
    mcp.prompt()(routing_system_prompt)

mcp =FastMCP("VideoProcessor")
add_mcp_prompts(mcp)
add_mcp_resource(mcp)
add_mcp_tool(mcp)


@click.command()
@click.option("--port", default=9090, help="FastMCP server port")
@click.option("--host", default="0.0.0.0", help="FastMCP server host")
@click.option("--transport", default="streamable-http", help="MCP Transport protocol type")
def run_mcp(port, host, transport):
    """
    Run the FastMCP server with the specified port, host, and transport protocol
    """
    mcp.run(host=host, port=port, transport=transport)


if __name__ == "__main__":
    run_mcp()