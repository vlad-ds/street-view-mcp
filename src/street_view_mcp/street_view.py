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

# Output directory for saving images (using absolute path to ensure it's in repo root)
OUTPUT_DIR = Path.cwd() / "output"


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
    filename: Optional[str] = None,
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
        filename (str, optional): If provided, save the image to this filename in the output directory
        
    Returns:
        PIL.Image: The Street View image
        
    Raises:
        ValueError: If no location method is provided or multiple are provided, or if filename already exists
        Exception: If the API request fails
    """
    # If filename is provided, check if it exists in output directory
    if filename:
        output_path = OUTPUT_DIR / filename
        if output_path.exists():
            raise ValueError(f"File {output_path} already exists")
    
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
            image = Image.open(BytesIO(response.content))
            
            # Save to file if filename is provided
            if filename:
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                
            return image
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
