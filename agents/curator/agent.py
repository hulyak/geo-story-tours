"""
Tour Curator Agent - Google ADK Implementation

Analyzes user preferences and selects optimal locations for personalized tours.
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore, pubsub_v1
import os
import json
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


def query_locations_tool(interests: List[str], max_locations: int = 8) -> str:
    """
    Query Firestore for locations matching user interests.

    Args:
        interests: List of interest categories (e.g., ["history", "art"])
        max_locations: Maximum number of locations to return

    Returns:
        JSON string of matching locations
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
            if any(interest in location_categories for interest in interests):
                matching.append(location)

        # Sort by relevance and limit
        def relevance_score(loc):
            categories = loc.get('categories', [])
            return sum(2 if cat in interests else 1 for cat in categories)

        matching.sort(key=relevance_score, reverse=True)
        selected = matching[:max_locations]

        return json.dumps(selected, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def create_tour_record_tool(tour_data: Dict[str, Any]) -> str:
    """
    Create initial tour record in Firestore.

    Args:
        tour_data: Tour information including locations and preferences

    Returns:
        Tour ID
    """
    try:
        tour_id = f"tour_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}"

        tour_record = {
            "tour_id": tour_id,
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
    1. Analyze their interests (e.g., history, art, food, hidden gems)
    2. Use the query_locations_tool to find matching locations
    3. Select 5-8 locations that best match their interests
    4. Consider their desired duration (typically 30 minutes)
    5. Create a tour record using create_tour_record_tool
    6. Publish the tour to the Route Optimizer using publish_to_optimizer_tool

    Be thoughtful about location selection:
    - Prioritize locations that match primary interests
    - Include 1-2 "surprise" locations from secondary interests
    - Ensure variety (don't select 8 history sites in a row)
    - Consider accessibility needs if specified

    Respond with a summary of the created tour including:
    - Tour ID
    - Number of locations selected
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
