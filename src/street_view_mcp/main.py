"""Entry point for the Street View MCP server."""

import argparse
import sys
# Use absolute import instead of relative import
from street_view_mcp.server import start_server

def main():
    """Run the Street View MCP server."""
    parser = argparse.ArgumentParser(description='Start the Street View MCP server.')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run the server on (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on (default: 8000)')

    args = parser.parse_args()

    try:
        print(f"Starting Street View MCP server on {args.host}:{args.port}")
        start_server(host=args.host, port=args.port)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    main()