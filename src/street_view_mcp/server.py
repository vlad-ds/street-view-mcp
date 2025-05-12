"""MCP Server wrapper for the Street View API."""

import io
from typing import Optional, Tuple, Dict, Any
from fastmcp import FastMCP, Image
from PIL import Image as PILImage

# Use absolute import instead of relative import
from street_view_mcp.street_view import get_street_view_image, get_panorama_metadata

# Initialize the MCP server
mcp = FastMCP("Street View MCP")

@mcp.tool()
def get_street_view(
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
    Fetch a Street View image based on location, coordinates, or panorama ID.
    
    Args:
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
    """
    # Parse lat_lng string to tuple if provided
    lat_lng_tuple = None
    if lat_lng:
        try:
            lat, lng = map(float, lat_lng.split(','))
            lat_lng_tuple = (lat, lng)
        except (ValueError, TypeError):
            raise ValueError("Invalid lat_lng format. Use format: '40.714728,-73.998672'")
            
    # Fetch the image
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

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the MCP server on the specified host and port."""
    mcp.start(host=host, port=port)

if __name__ == "__main__":
    start_server()