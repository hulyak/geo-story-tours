"""
Tour Curator Agent - Google ADK Implementation

Analyzes user preferences and selects optimal locations for personalized tours.
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore, pubsub_v1
import os
import json
import random
import math
from datetime import datetime
from typing import Dict, List, Any, Optional

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers.

    Args:
        lat1, lon1: Latitude and longitude of first point in decimal degrees
        lat2, lon2: Latitude and longitude of second point in decimal degrees

    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    r = 6371

    return c * r


def query_locations_tool(
    interests: List[str],
    center_lat: Optional[float] = None,
    center_lng: Optional[float] = None,
    max_radius_km: float = 5.0,
    max_locations: int = 8
) -> str:
    """
    Query Firestore for locations matching user interests and within geographical radius.

    Args:
        interests: List of interest categories (e.g., ["history", "art"])
        center_lat: Latitude of center point for proximity filtering
        center_lng: Longitude of center point for proximity filtering
        max_radius_km: Maximum distance in kilometers from center point (default 5km)
        max_locations: Maximum number of locations to return

    Returns:
        JSON string of matching locations with distance information
    """
    try:
        locations_ref = firestore_client.collection('locations')
        all_locations = list(locations_ref.limit(100).stream())

        matching = []
        for doc in all_locations:
            location = doc.to_dict()
            location['id'] = doc.id

            # Check if location matches interests
            location_categories = location.get('categories', [])
            if not any(interest in location_categories for interest in interests):
                continue

            # Calculate distance if center coordinates provided
            if center_lat is not None and center_lng is not None:
                coords = location.get('coordinates', {})
                loc_lat = coords.get('lat')
                loc_lng = coords.get('lng')

                if loc_lat is None or loc_lng is None:
                    continue

                distance_km = haversine_distance(center_lat, center_lng, loc_lat, loc_lng)

                # Skip locations outside radius
                if distance_km > max_radius_km:
                    continue

                location['distance_km'] = round(distance_km, 2)
            else:
                location['distance_km'] = None

            matching.append(location)

        # Sort by relevance with distance consideration
        def relevance_score(loc):
            categories = loc.get('categories', [])
            base_score = sum(2 if cat in interests else 1 for cat in categories)

            # Factor in distance (closer is better)
            distance = loc.get('distance_km', 0)
            if distance and distance > 0:
                distance_penalty = 1 / (1 + distance * 0.2)  # Gentle penalty for distance
            else:
                distance_penalty = 1.0

            # Add randomness (10-30% variation) to create diverse tours
            diversity_factor = random.uniform(0.8, 1.2)

            return base_score * distance_penalty * diversity_factor

        matching.sort(key=relevance_score, reverse=True)
        selected = matching[:max_locations]

        return json.dumps(selected, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def create_tour_record_tool(tour_data: Dict[str, Any]) -> str:
    """
    Create initial tour record in Firestore.

    Args:
        tour_data: Tour information including locations and preferences.
                   Must include 'tour_id' field.

    Returns:
        Tour ID
    """
    try:
        # Use the tour_id from tour_data instead of generating a new one
        tour_id = tour_data.get('tour_id')
        if not tour_id:
            return "Error: tour_id is required in tour_data"

        tour_record = {
            "status": "route_planning",
            "created_at": datetime.now().isoformat(),
            **tour_data
        }

        tours_ref = firestore_client.collection('tours')
        tours_ref.document(tour_id).set(tour_record)

        return tour_id

    except Exception as e:
        return f"Error: {str(e)}"


def publish_to_optimizer_tool(tour_id: str, tour_data: Dict[str, Any]) -> str:
    """
    Publish tour to Route Optimizer Agent via Pub/Sub.

    Args:
        tour_id: Tour identifier
        tour_data: Complete tour data

    Returns:
        Success message with Pub/Sub message ID
    """
    try:
        topic_path = publisher.topic_path(PROJECT_ID, 'route-planned')

        message = {
            "tour_id": tour_id,
            **tour_data
        }

        message_data = json.dumps(message, default=str).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()

        return f"Published to route-planned: {message_id}"

    except Exception as e:
        return f"Error: {str(e)}"


# Define the Tour Curator Agent using Google ADK
curator_agent = Agent(
    name="tour_curator_agent",
    model="gemini-2.5-flash",

    instruction="""
    You are the Tour Curator Agent for Geo-Story Micro-Tours.

    Your job is to create personalized tour routes based on user preferences.

    When a user requests a tour, you should:
    1. Extract the Tour ID from the prompt (it will be provided as "Tour ID: tour_xxxxx")
    2. Analyze their interests (e.g., history, art, food, hidden gems)
    3. Extract starting location coordinates (latitude, longitude) from the user prompt
    4. Use the query_locations_tool to find matching locations within walking distance (5km radius)
       - ALWAYS provide center_lat and center_lng parameters to filter by proximity
       - This ensures all locations in the tour are geographically close
    5. Select 5-8 locations that best match their interests AND are within walking distance
    6. Consider their desired duration (typically 30 minutes)
    7. Create a tour record using create_tour_record_tool
       - IMPORTANT: You MUST include the tour_id (from step 1) in the tour_data dictionary
       - The tour_data must contain: tour_id, interests, duration, locations
    8. Publish the tour to the Route Optimizer using publish_to_optimizer_tool

    Be thoughtful about location selection:
    - Prioritize locations that match primary interests
    - Include 1-2 "surprise" locations from secondary interests
    - Ensure variety (don't select 8 history sites in a row)
    - Consider accessibility needs if specified
    - IMPORTANT: All locations MUST be within the same geographical area (5km radius)
    - Never mix locations from different cities (e.g., Paris and New York)

    Respond with a summary of the created tour including:
    - Tour ID (use the one provided in the prompt)
    - Number of locations selected
    - Geographical area covered
    - Estimated total time
    - Categories covered
    """,

    description="Curates personalized tour routes by analyzing preferences and selecting optimal locations",

    tools=[
        query_locations_tool,
        create_tour_record_tool,
        publish_to_optimizer_tool
    ]
)


# Export for deployment
agent = curator_agent

if __name__ == "__main__":
    print(f"✅ Tour Curator Agent initialized: {agent.name}")
    print(f"📦 Model: {agent.model}")
    print(f"🔧 Tools: {len(agent.tools)}")
