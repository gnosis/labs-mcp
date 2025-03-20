from mcp.server.fastmcp.server import FastMCP


mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def mul(a: int, b: int) -> int:
    """Add two numbers"""
    return a * b

