"""Module for interacting with Google Street View API."""

import os
import sys
import argparse
import requests
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Tuple
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv("API_KEY")


def get_street_view_image(
    location: Optional[str] = None,
    lat_lng: Optional[Tuple[float, float]] = None,
    pano_id: Optional[str] = None,
    size: str = "600x400",
    heading: int = 0,
    pitch: int = 0,
    fov: int = 90,
    radius: int = 50,
    source: str = "default",
    return_error_code: bool = True,
):
    """
    Fetch a Street View image using various location specifiers.
    
    Args:
        location (str, optional): The address to get Street View image for
        lat_lng (tuple, optional): Latitude and longitude coordinates as (lat, lng)
        pano_id (str, optional): Specific panorama ID to fetch
        size (str): The size of the image in pixels as 'widthxheight'
        heading (int): Camera heading in degrees relative to true north
        pitch (int): Camera pitch in degrees, relative to the street view vehicle
        fov (int): Field of view in degrees (zoom level)
        radius (int): Search radius in meters (when using location or lat_lng)
        source (str): Limits Street View searches to selected sources (default, outdoor)
        return_error_code (bool): Whether to return error codes instead of generic images
        
    Returns:
        PIL.Image: The Street View image
        
    Raises:
        ValueError: If no location method is provided or multiple are provided
        Exception: If the API request fails
    """
    # Validate input: exactly one location method must be provided
    location_methods = sum(1 for m in [location, lat_lng, pano_id] if m is not None)
    if location_methods == 0:
        raise ValueError("Must provide one of: location, lat_lng, or pano_id")
    if location_methods > 1:
        raise ValueError("Provide only one of: location, lat_lng, or pano_id")
    
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    
    params = {
        "size": size,
        "heading": heading,
        "pitch": pitch,
        "fov": fov,
        "radius": radius,
        "source": source,
        "return_error_code": str(return_error_code).lower(),
        "key": API_KEY,
    }
    
    # Set the location parameter based on what was provided
    if location:
        params["location"] = location
    elif lat_lng:
        params["location"] = f"{lat_lng[0]},{lat_lng[1]}"
    elif pano_id:
        params["pano"] = pano_id
        # Remove radius when using pano_id as it's not applicable
        if "radius" in params:
            del params["radius"]
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        if response.headers.get('content-type', '').startswith('image/'):
            return Image.open(BytesIO(response.content))
        else:
            raise Exception("Received non-image response from API")
    else:
        raise Exception(f"Error fetching Street View image: {response.status_code}")


def get_panorama_metadata(
    location: Optional[str] = None,
    lat_lng: Optional[Tuple[float, float]] = None,
    pano_id: Optional[str] = None,
    radius: int = 50,
    source: str = "default",
):
    """
    Fetch metadata about a Street View panorama to check availability.
    
    Args:
        location (str, optional): The address to check for Street View imagery
        lat_lng (tuple, optional): Latitude and longitude coordinates as (lat, lng)
        pano_id (str, optional): Specific panorama ID to fetch metadata for
        radius (int): Search radius in meters (when using location or lat_lng)
        source (str): Limits Street View searches to selected sources (default, outdoor)
        
    Returns:
        dict: Panorama metadata including status, copyright, date, pano_id, lat, lng
        
    Raises:
        ValueError: If no location method is provided or multiple are provided
        Exception: If the API request fails
    """
    # Validate input: exactly one location method must be provided
    location_methods = sum(1 for m in [location, lat_lng, pano_id] if m is not None)
    if location_methods == 0:
        raise ValueError("Must provide one of: location, lat_lng, or pano_id")
    if location_methods > 1:
        raise ValueError("Provide only one of: location, lat_lng, or pano_id")
    
    base_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    
    params = {
        "radius": radius,
        "source": source,
        "key": API_KEY,
    }
    
    # Set the location parameter based on what was provided
    if location:
        params["location"] = location
    elif lat_lng:
        params["location"] = f"{lat_lng[0]},{lat_lng[1]}"
    elif pano_id:
        params["pano"] = pano_id
        # Remove radius when using pano_id as it's not applicable
        if "radius" in params:
            del params["radius"]
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching Street View metadata: {response.status_code}")


def save_street_view_image(
    output_path: str,
    location: Optional[str] = None,
    lat_lng: Optional[Tuple[float, float]] = None,
    pano_id: Optional[str] = None,
    **kwargs
):
    """
    Fetch a Street View image and save it to disk.
    
    Args:
        output_path (str): Path to save the image
        location (str, optional): The address to get Street View image for
        lat_lng (tuple, optional): Latitude and longitude coordinates as (lat, lng)
        pano_id (str, optional): Specific panorama ID to fetch
        **kwargs: Additional parameters to pass to get_street_view_image
        
    Returns:
        str: Path to the saved image
        
    Raises:
        ValueError: If no location method is provided or multiple are provided
    """
    # Pass all location methods to get_street_view_image
    # The function will validate that exactly one is provided
    image = get_street_view_image(
        location=location,
        lat_lng=lat_lng,
        pano_id=pano_id,
        **kwargs
    )
    
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save the image
    image.save(output_path)
    
    return output_path


def open_image(image_path):
    """
    Open an image with the default system viewer.
    
    Args:
        image_path (str): Path to the image to open
        
    Returns:
        bool: True if opened successfully, False otherwise
    """
    try:
        if os.name == 'nt':  # Windows
            os.system(f'start {image_path}')
        elif os.name == 'posix':  # macOS or Linux
            if os.uname().sysname == 'Darwin':  # macOS
                os.system(f'open {image_path}')
            else:  # Linux
                os.system(f'xdg-open {image_path}')
        return True
    except Exception as e:
        print(f"Couldn't open image automatically: {e}")
        print(f"Please open {image_path} manually to view the image.")
        return False


def main():
    """Run as a command-line tool."""
    parser = argparse.ArgumentParser(description='Fetch and save Google Street View images.')
    
    # Create a mutually exclusive group for location specifiers
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument('--address', help='Address to fetch Street View image for')
    location_group.add_argument('--latlong', '--latlng', help='Latitude,longitude coordinates (e.g., "40.714728,-73.998672")')
    location_group.add_argument('--pano', help='Specific panorama ID to fetch')
    
    # Image parameters
    parser.add_argument('--output', '-o', default='street_view.jpg', help='Output path for saved image (default: street_view.jpg)')
    parser.add_argument('--size', default='600x400', help='Image size in widthxheight format (default: 600x400)')
    parser.add_argument('--heading', type=int, default=0, help='Camera heading in degrees (default: 0)')
    parser.add_argument('--pitch', type=int, default=0, help='Camera pitch in degrees (default: 0)')
    parser.add_argument('--fov', type=int, default=90, help='Field of view in degrees (default: 90)')
    parser.add_argument('--radius', type=int, default=50, help='Search radius in meters (default: 50)')
    parser.add_argument('--source', choices=['default', 'outdoor'], default='default', 
                        help='Limits searches to selected sources (default: "default")')
    
    # Utility options
    parser.add_argument('--open', action='store_true', help='Open image after download (default: False)')
    parser.add_argument('--metadata', action='store_true', help='Just fetch metadata, don\'t download image (default: False)')
    
    args = parser.parse_args()
    
    try:
        # Parse latitude,longitude if provided
        lat_lng = None
        if args.latlong:
            try:
                lat, lng = map(float, args.latlong.split(','))
                lat_lng = (lat, lng)
                location_desc = f"({lat}, {lng})"
            except ValueError:
                raise ValueError("Invalid latitude,longitude format. Use format: 40.714728,-73.998672")
        elif args.address:
            location_desc = args.address
        else:  # pano
            location_desc = f"panorama {args.pano}"
            
        # If metadata only, fetch and display metadata
        if args.metadata:
            print(f"Fetching Street View metadata for: {location_desc}")
            metadata = get_panorama_metadata(
                location=args.address,
                lat_lng=lat_lng,
                pano_id=args.pano,
                radius=args.radius,
                source=args.source,
            )
            print("Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
            return 0
            
        # Otherwise, fetch and save the image
        print(f"Fetching Street View image for: {location_desc}")
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_dir = output_path.parent
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get and save the image
        saved_path = save_street_view_image(
            str(output_path),
            location=args.address,
            lat_lng=lat_lng,
            pano_id=args.pano,
            size=args.size,
            heading=args.heading,
            pitch=args.pitch,
            fov=args.fov,
            radius=args.radius,
            source=args.source,
        )
        
        print(f"Image saved to: {saved_path}")
        
        # Open the image if requested
        if args.open:
            open_image(saved_path)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())