# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

- We have a uv venv. Enable it if not enabled.
- Install dependencies with:
  ```bash
  uv pip install -e ".[dev]"
  ```

## Usage Commands

### Testing
```bash
pytest
```

### Running the MCP Server
```bash
python -m street_view_mcp.main --host 127.0.0.1 --port 8000
```

### Using as a CLI Tool
```bash
python -m street_view_mcp.street_view --address "Empire State Building, NY" --output output/empire_state.jpg
# or
python -m street_view_mcp.street_view --latlong "40.748817,-73.985428" --output output/coords.jpg --heading 180
# or
python -m street_view_mcp.street_view --pano PANO_ID --output output/panorama.jpg
```

## Architecture Overview

The Street View MCP is structured as:

1. **Core API Client** (`street_view.py`):
   - Handles direct interactions with Google Street View API
   - Manages image fetching, metadata retrieval, and image saving
   - Requires an API key stored in the environment variable `API_KEY`

2. **MCP Server** (`server.py`):
   - Wraps the core functionality in a FastMCP server
   - Provides two main tools:
     - `get_street_view` - Fetches and returns Street View images
     - `get_metadata` - Retrieves metadata about Street View panoramas

3. **Entry Points**:
   - CLI: `street_view_mcp.street_view`
   - Server: `street_view_mcp.main`

## API Requirements

- Requires a Google Maps API key with Street View API enabled
- The API key should be set as an environment variable named `API_KEY`