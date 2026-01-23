import click
from fastmcp import FastMCP




mcp =FastMCP("VideoProcessor")

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