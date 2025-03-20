from server.app import mcp


def main():
    print('Starting MCP server...')
    mcp.run(transport="sse")

if __name__ == "__main__":
    main()