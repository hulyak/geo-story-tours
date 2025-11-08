"""
Route Optimizer Agent - Google ADK Implementation

Calculates optimal walking paths between tour locations.
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore, pubsub_v1
import os
import json
import math
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


def calculate_route_tool(locations: List[Dict[str, Any]], start_location: Dict[str, float]) -> str:
    """
    Calculate optimal walking route using nearest neighbor algorithm.

    Args:
        locations: List of locations to visit
        start_location: Starting point {lat, lng}

    Returns:
        JSON string of optimized route with walking distances and times
    """
    try:
        def haversine_distance(point1, point2):
            """Calculate distance in meters between two GPS points"""
            lat1, lon1 = math.radians(point1['lat']), math.radians(point1['lng'])
            lat2, lon2 = math.radians(point2['lat']), math.radians(point2['lng'])

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))

            return c * 6371000  # Earth radius in meters

        # Optimize route using nearest neighbor
        optimized_route = []
        remaining = locations.copy()
        current_pos = start_location
        walking_speed = 80  # meters per minute

        while remaining:
            # Find nearest location
            nearest = min(remaining, key=lambda loc: haversine_distance(
                current_pos,
                loc.get('coordinates', {})
            ))

            # Calculate walking info
            distance = haversine_distance(current_pos, nearest.get('coordinates', {}))
            walking_minutes = distance / walking_speed

            nearest['route_info'] = {
                "distance_meters": round(distance, 1),
                "walking_minutes": round(walking_minutes, 1),
                "from_previous": optimized_route[-1]['name'] if optimized_route else "start"
            }

            optimized_route.append(nearest)
            remaining.remove(nearest)
            current_pos = nearest.get('coordinates', {})

        # Calculate totals
        total_walking = sum(loc.get('route_info', {}).get('walking_minutes', 0) for loc in optimized_route)
        total_story = sum(loc.get('average_visit_minutes', 5) for loc in optimized_route)

        result = {
            "optimized_locations": optimized_route,
            "duration_info": {
                "walking_minutes": round(total_walking),
                "story_minutes": round(total_story),
                "total_minutes": round(total_walking + total_story)
            }
        }

        return json.dumps(result, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def update_tour_record_tool(tour_id: str, optimized_data: Dict[str, Any]) -> str:
    """
    Update tour record with optimized route.

    Args:
        tour_id: Tour identifier
        optimized_data: Optimized route and duration info

    Returns:
        Success message
    """
    try:
        tours_ref = firestore_client.collection('tours')
        tours_ref.document(tour_id).update({
            "status": "route_optimized",
            "route_optimized_at": datetime.now().isoformat(),
            **optimized_data
        })

        return f"Tour {tour_id} updated successfully"

    except Exception as e:
        return f"Error: {str(e)}"


def publish_to_storyteller_tool(tour_id: str, tour_data: Dict[str, Any]) -> str:
    """
    Publish optimized tour to Storytelling Agent.

    Args:
        tour_id: Tour identifier
        tour_data: Complete tour data with optimized route

    Returns:
        Success message
    """
    try:
        topic_path = publisher.topic_path(PROJECT_ID, 'route-optimized')

        message = {
            "tour_id": tour_id,
            **tour_data
        }

        message_data = json.dumps(message, default=str).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()

        return f"Published to route-optimized: {message_id}"

    except Exception as e:
        return f"Error: {str(e)}"


# Define the Route Optimizer Agent using Google ADK
optimizer_agent = Agent(
    name="route_optimizer_agent",
    model="gemini-2.5-flash",

    instruction="""
    You are the Route Optimizer Agent for Geo-Story Micro-Tours.

    Your job is to calculate optimal walking routes between locations.

    When you receive a tour from the Curator Agent, you should:
    1. Extract the list of locations
    2. Use calculate_route_tool to optimize the walking path
    3. Update the tour record with optimized route using update_tour_record_tool
    4. Publish to the Storytelling Agent using publish_to_storyteller_tool

    The calculate_route_tool uses the nearest neighbor algorithm to minimize
    total walking distance while ensuring a logical flow between locations.

    Provide a summary including:
    - Total walking distance
    - Total walking time
    - Total story time
    - Estimated completion time
    """,

    description="Calculates optimal walking paths between tour locations using distance algorithms",

    tools=[
        calculate_route_tool,
        update_tour_record_tool,
        publish_to_storyteller_tool
    ]
)


# Export for deployment
agent = optimizer_agent

if __name__ == "__main__":
    print(f"✅ Route Optimizer Agent initialized: {agent.name}")
    print(f"📦 Model: {agent.model}")
    print(f"🔧 Tools: {len(agent.tools)}")
