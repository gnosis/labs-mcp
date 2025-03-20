from labs_mcp.server import mcp

def main():
    print('Starting MCP server...')
    mcp.run(transport="sse")
