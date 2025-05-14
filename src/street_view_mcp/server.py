"""MCP Server wrapper for the Street View API."""

import io
import os
import sys
import webbrowser
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Union, List
from fastmcp import FastMCP, Image
from PIL import Image as PILImage

# Use absolute import instead of relative import
from street_view_mcp.street_view import get_street_view_image, get_panorama_metadata

# Output directories (using absolute paths to ensure they're in repo root)
OUTPUT_DIR = Path.cwd() / "output"
HTML_DIR = Path.cwd() / "html"

# Initialize the MCP server
mcp = FastMCP("Street View MCP")

@mcp.tool()
def get_street_view(
    filename: str,
    location: Optional[str] = None,
    lat_lng: Optional[str] = None,
    pano_id: Optional[str] = None,
    size: str = "600x400",
    heading: int = 0,
    pitch: int = 0,
    fov: int = 90,
    radius: int = 50,
    source: str = "default",
) -> Image:
    """
    Fetch a Street View image based on location, coordinates, or panorama ID and save to file.
    
    Args:
        filename: Required filename to save the image (must not already exist in output directory)
        location: The address to get Street View image for (e.g., "Empire State Building, NY")
        lat_lng: Comma-separated latitude and longitude (e.g., "40.748817,-73.985428")
        pano_id: Specific panorama ID to fetch
        size: Image dimensions as "widthxheight" (e.g., "600x400")
        heading: Camera heading in degrees (0-360)
        pitch: Camera pitch in degrees (-90 to 90)
        fov: Field of view in degrees (zoom level, 10-120)
        radius: Search radius in meters when using location or coordinates
        source: Limit Street View searches to selected sources ("default" or "outdoor")
        
    Returns:
        Image: The Street View image
        
    Raises:
        ValueError: If filename already exists in output directory
    """
    # Parse lat_lng string to tuple if provided
    lat_lng_tuple = None
    if lat_lng:
        try:
            lat, lng = map(float, lat_lng.split(','))
            lat_lng_tuple = (lat, lng)
        except (ValueError, TypeError):
            raise ValueError("Invalid lat_lng format. Use format: '40.714728,-73.998672'")
            
    # Fetch the image and save it
    pil_image = get_street_view_image(
        location=location,
        lat_lng=lat_lng_tuple,
        pano_id=pano_id,
        size=size,
        heading=heading,
        pitch=pitch,
        fov=fov,
        radius=radius,
        source=source,
        return_error_code=True,
        filename=filename,
    )
    
    # Convert PIL Image to bytes
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    
    # Return using FastMCP's Image helper
    return Image(data=img_bytes, format="jpeg")

@mcp.tool()
def get_metadata(
    location: Optional[str] = None,
    lat_lng: Optional[str] = None,
    pano_id: Optional[str] = None,
    radius: int = 50,
    source: str = "default",
) -> Dict[str, Any]:
    """
    Fetch metadata about a Street View panorama.
    
    Args:
        location: The address to check for Street View imagery
        lat_lng: Comma-separated latitude and longitude (e.g., "40.748817,-73.985428")
        pano_id: Specific panorama ID to fetch metadata for
        radius: Search radius in meters when using location or coordinates
        source: Limit Street View searches to selected sources ("default" or "outdoor")
        
    Returns:
        Dict: Panorama metadata including status, copyright, date, pano_id, lat, lng
    """
    # Parse lat_lng string to tuple if provided
    lat_lng_tuple = None
    if lat_lng:
        try:
            lat, lng = map(float, lat_lng.split(','))
            lat_lng_tuple = (lat, lng)
        except (ValueError, TypeError):
            raise ValueError("Invalid lat_lng format. Use format: '40.714728,-73.998672'")
    
    # Fetch metadata
    return get_panorama_metadata(
        location=location,
        lat_lng=lat_lng_tuple,
        pano_id=pano_id,
        radius=radius,
        source=source,
    )

@mcp.tool()
def open_image_locally(filename: str) -> Dict[str, str]:
    """
    Open a saved Street View image in the default application.
    
    Args:
        filename: The filename of the image to open (must exist in output directory)
        
    Returns:
        Dict: A status message indicating success or failure
        
    Raises:
        ValueError: If the file doesn't exist in the output directory
    """
    # Check if file exists
    image_path = OUTPUT_DIR / filename
    if not image_path.exists():
        raise ValueError(f"Image file '{filename}' does not exist in the output directory")
    
    # Convert to absolute path
    abs_path = image_path.absolute().as_uri()
    
    # Open in local application
    webbrowser.open(abs_path)
    
    return {"status": "success", "message": f"Opened {filename} in default application"}


@mcp.tool()
def create_html_page(html_elements: List[str], filename: str) -> Dict[str, str]:
    """
    Create an HTML page from a list of HTML elements and open it in the default browser.
    
    Args:
        html_elements: List of HTML element strings to be combined
        filename: Name of the HTML file to create (without directory path)
        
    Returns:
        Dict: A status message indicating success or failure
        
    Raises:
        ValueError: If the filename already exists or is invalid
        
    Note:
        To include Street View images in your HTML, reference them with relative paths:
        - For an image saved as "empire.jpg" in the output directory:
          `<img src="..output/empire.jpg" alt="Empire State Building">`
        - The path is relative to the repository root where both output/ and html/ directories are located
        - Example usage:
          ```
          html_elements = [
              "<h1>My Tour Guide</h1>",
              "<p>Welcome to New York City!</p>",
              "<img src='../output/empire.jpg' alt='Empire State Building'>",
              "<p>The Empire State Building is an iconic landmark.</p>"
          ]
          ```
    """
    # Validate filename
    if not filename.endswith('.html'):
        filename += '.html'
    
    # Create full path
    file_path = HTML_DIR / filename
    
    # Check if file already exists
    if file_path.exists():
        raise ValueError(f"File {file_path} already exists")
    
    # Ensure directory exists
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    
    # Combine HTML elements
    html_content = ''.join(html_elements)
    
    # Write to file
    with open(file_path, 'w') as f:
        f.write(html_content)
    
    # Open in browser
    abs_path = file_path.absolute().as_uri()
    webbrowser.open(abs_path)
    
    return {"status": "success", "message": f"Created and opened {filename}"}


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the MCP server on the specified host and port."""
    mcp.start(host=host, port=port)

if __name__ == "__main__":
    start_server()