# Street View MCP

A Model-Client-Protocol (MCP) server for Google Street View API that enables AI models to fetch and display street view imagery and create virtual tours.

## Using with Claude Desktop

To use Street View MCP with Claude Desktop:

1. Ensure you have `uv` installed: [UV Installation Guide](https://github.com/astral-sh/uv)
2. Clone this repository:
   ```bash
   git clone https://github.com/vlad-ds/street-view-mcp.git
   cd street-view-mcp
   ```
3. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
4. Get a Google Maps API key (instructions below)
5. Add the following to your Claude Desktop `claude_desktop_config.json` file:

```json
"street_view": {
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/path/to/street-view-mcp",  // Replace with your actual path
    "mcp",
    "run",
    "src/street_view_mcp/server.py"
  ],
  "env": {
    "API_KEY": "your_google_maps_api_key_here"  // Add your API key here
  }
}
```

After configuration, you can use Street View MCP in Claude Desktop simply by typing "/street_view".

## Overview

Street View MCP provides a simple interface for AI models to:
1. Fetch Street View images by address, coordinates, or panorama ID
2. Save images to local files
3. Open saved images in the default viewer
4. Create HTML pages that compile multiple Street View images into virtual tours

## Requirements

- Python 3.9+
- Google Maps API key with Street View API enabled
- `fastmcp` package
- `uv` package manager (recommended)

## Installation

```bash
# Clone the repository
git clone https://github.com/vlad-ds/street-view-mcp.git
cd street-view-mcp

# Create and activate a virtual environment with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

## API Key Setup

The Street View MCP requires a Google Maps API key with Street View API enabled:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Street View Static API" in the API Library
4. Create an API key from the Credentials page
5. Set the API key as an environment variable:

```bash
# Set temporarily in your shell:
export API_KEY=your_api_key_here

# Or create a .env file in the project root:
echo "API_KEY=your_api_key_here" > .env
```

## Usage

### Starting the MCP Server

```bash
python -m street_view_mcp.main --host 127.0.0.1 --port 8000
```

The server will be available to AI models at the specified host and port.

### Using as a CLI Tool

```bash
# Fetch Street View image by address
python -m street_view_mcp.street_view --address "Empire State Building, NY" --output output/empire_state.jpg

# Fetch Street View image by latitude/longitude
python -m street_view_mcp.street_view --latlong "40.748817,-73.985428" --output output/coords.jpg --heading 180

# Fetch Street View image by panorama ID
python -m street_view_mcp.street_view --pano PANO_ID --output output/panorama.jpg
```

## MCP Tools

The Street View MCP provides the following tools for AI models:

### `get_street_view`

Fetches a Street View image based on location, coordinates, or panorama ID and saves it to a file.

```python
{
  "filename": "empire_state.jpg",
  "location": "Empire State Building, NY",
  "size": "600x400",
  "heading": 90,
  "pitch": 10
}
```

Parameters:
- `filename` (required): Name for saving the image (must not already exist)
- `location` (optional): Address to get image for 
- `lat_lng` (optional): Comma-separated coordinates (e.g., "40.748817,-73.985428")
- `pano_id` (optional): Specific panorama ID
- `size` (optional): Image dimensions as "widthxheight" (default: "600x400")
- `heading` (optional): Camera heading in degrees (0-360, default: 0)
- `pitch` (optional): Camera pitch in degrees (-90 to 90, default: 0)
- `fov` (optional): Field of view in degrees (10-120, default: 90)
- `radius` (optional): Search radius in meters (default: 50)
- `source` (optional): Image source ("default" or "outdoor", default: "default")

Note: Exactly one of `location`, `lat_lng`, or `pano_id` must be provided.

### `get_metadata`

Fetches metadata about a Street View panorama.

```python
{
  "location": "Empire State Building, NY"
}
```

Parameters:
- Same location parameters as `get_street_view`
- Returns JSON metadata with status, copyright, date, panorama ID, and coordinates

### `open_image_locally`

Opens a saved Street View image in the default application.

```python
{
  "filename": "empire_state.jpg"
}
```

Parameters:
- `filename` (required): The filename of the image to open (must exist in output directory)

### `create_html_page`

Creates an HTML page that displays multiple Street View images as a virtual tour.

```python
{
  "filename": "nyc_tour.html",
  "title": "New York City Tour",
  "html_elements": [
    "<h1>New York City Landmarks Tour</h1>",
    "<p>Explore famous landmarks through Street View images.</p>",
    "<h2>Empire State Building</h2>",
    "<img src='../output/empire.jpg' alt='Empire State Building'>",
    "<p class='location'>350 Fifth Avenue, New York, NY</p>",
    "<p class='description'>This 102-story Art Deco skyscraper was completed in 1931.</p>"
  ]
}
```

Parameters:
- `html_elements` (required): List of HTML content elements
- `filename` (required): Name for the HTML file
- `title` (optional): Page title (default: "Street View Tour")

Important: When referencing images, always use the path `../output/filename.jpg`.

## Creating Virtual Tours

The Street View MCP enables creation of virtual tours by combining multiple Street View images with descriptive text in an HTML page.

Example workflow for creating a tour:

1. Fetch images of different locations:
```python
get_street_view(filename="empire.jpg", location="Empire State Building, NY")
get_street_view(filename="times_square.jpg", location="Times Square, NY")
get_street_view(filename="central_park.jpg", location="Central Park, NY")
```

2. Create an HTML tour page:
```python
create_html_page(
  filename="nyc_tour.html",
  title="New York City Tour",
  html_elements=[
    "<h1>New York City Landmarks Tour</h1>",
    "<p>Explore these famous NYC landmarks through Street View images.</p>",
    
    "<h2>Empire State Building</h2>",
    "<img src='../output/empire.jpg' alt='Empire State Building'>",
    "<p class='location'>350 Fifth Avenue, New York, NY</p>",
    "<p class='description'>An iconic 102-story Art Deco skyscraper in Midtown Manhattan.</p>",
    
    "<h2>Times Square</h2>",
    "<img src='../output/times_square.jpg' alt='Times Square'>",
    "<p class='location'>Broadway & 7th Avenue, New York, NY</p>",
    "<p class='description'>Famous for its bright lights, Broadway theaters, and as the site of the annual New Year's Eve ball drop.</p>",
    
    "<h2>Central Park</h2>",
    "<img src='../output/central_park.jpg' alt='Central Park'>",
    "<p class='location'>Central Park, New York, NY</p>",
    "<p class='description'>An urban park spanning 843 acres in the heart of Manhattan.</p>"
  ]
)
```

## Project Structure

- `street_view_mcp/`
  - `__init__.py`: Package initialization
  - `main.py`: Entry point for MCP server
  - `server.py`: MCP server implementation
  - `street_view.py`: Core Street View API client

## Important Notes

- **Local Storage**: This tool saves all Street View images and HTML files locally in the `output/` directory
- **No Automatic Cleanup**: There is no built-in mechanism to delete saved files
- **Manual Cleanup**: You should periodically clean up the `output/` directory to manage disk space
- **API Usage**: Each image request counts toward your Google Maps API quota and may incur charges

## Development

### Testing

```bash
pytest
```

## License

MIT