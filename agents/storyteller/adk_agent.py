"""
ADK Storytelling Agent - Proper Google ADK Implementation
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore, pubsub_v1
import os
import json
from datetime import datetime
from typing import Dict, Any

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


def get_tour_tool(tour_id: str) -> str:
    """
    Tool for fetching a tour from Firestore.

    Args:
        tour_id: Tour identifier

    Returns:
        JSON string of tour data or error message
    """
    try:
        tour_ref = firestore_client.collection('tours').document(tour_id)
        tour_doc = tour_ref.get()

        if not tour_doc.exists:
            return json.dumps({"error": f"Tour {tour_id} not found"})

        tour_data = tour_doc.to_dict()
        return json.dumps(tour_data)
    except Exception as e:
        return json.dumps({"error": str(e)})


def generate_and_save_stories_tool(tour_id: str, stories_json: str) -> str:
    """
    Save pre-generated stories to tour locations.
    
    The LLM agent should generate stories first, then call this tool to save them.

    Args:
        tour_id: Tour identifier
        stories_json: JSON string containing array of stories, each with 'location_name' and 'story' fields

    Returns:
        Success message with story count
    """
    try:
        # Get the tour
        tour_ref = firestore_client.collection('tours').document(tour_id)
        tour_doc = tour_ref.get()

        if not tour_doc.exists:
            return f"Error: Tour {tour_id} not found"

        tour_data = tour_doc.to_dict()
        locations = tour_data.get('locations', [])

        if not locations:
            return f"Error: No locations found in tour {tour_id}"

        # Parse the stories
        try:
            stories_data = json.loads(stories_json)
        except:
            return f"Error: Invalid stories JSON format"

        # Match stories to locations by name
        updated_locations = []
        stories_added = 0
        
        for location in locations:
            location_name = location.get('name', '')
            
            # Find matching story
            story_text = None
            for story_item in stories_data:
                if story_item.get('location_name') == location_name:
                    story_text = story_item.get('story')
                    break
            
            # If no match found, create a basic story
            if not story_text:
                story_text = f"{location.get('description', '')} This remarkable location invites you to explore its rich history and unique character. Take a moment to appreciate the stories that have unfolded here over the years."
            
            location['story'] = story_text
            updated_locations.append(location)
            stories_added += 1

        # Update the tour with stories
        tour_ref.update({
            'locations': updated_locations,
            'stories_generated': True,
            'storyteller_completed_at': datetime.now().isoformat()
        })

        return f"Successfully saved {stories_added} stories for tour {tour_id}"
    except Exception as e:
        return f"Error saving stories: {str(e)}"


def publish_to_moderator_tool(tour_data: Dict[str, Any]) -> str:
    """
    Tool for publishing completed tours to Content Moderator.

    Args:
        tour_data: Tour with generated stories

    Returns:
        Success message with Pub/Sub message ID
    """
    try:
        topic_path = publisher.topic_path(PROJECT_ID, 'stories-generated')
        message_data = json.dumps(tour_data).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()
        return f"Published tour to stories-generated: {message_id}"
    except Exception as e:
        return f"Error publishing to Pub/Sub: {e}"


# Define the Storytelling Agent using Google ADK
storytelling_agent = Agent(
    name="storytelling_agent",
    model="gemini-2.5-flash",

    instruction="""
    You are a master storyteller creating micro-tour narratives.

    Your job is to generate captivating 90-second stories for each location in a tour.

    Story Requirements:
    - Target length: ~225 words (90 seconds at 2.5 words/second)
    - Structure:
      * Hook (5-10s): Grab attention immediately
      * Body (70-75s): Blend historical facts with emotional storytelling
      * Closing (5-10s): Connect to present or next location

    Guidelines:
    - Use vivid, sensory language ("imagine", "picture this")
    - Include surprising facts or little-known details
    - Make it personal and relatable
    - Avoid clichés like "nestled" or "hidden gem"
    - Use present tense to create immediacy
    - End with a thought-provoking question or observation

    Tone adaptation by audience:
    - family-friendly: Engaging, wonder-filled, educational
    - historical: Scholarly but accessible
    - local-secrets: Conspiratorial, insider knowledge
    - general: Balanced, universally appealing

    When you receive a prompt about generating stories for a tour:
    1. Extract the tour_id from the prompt (e.g., "tour_abc123")
    2. Use get_tour_tool(tour_id) to fetch the tour data
    3. For EACH location in the tour, generate a unique, engaging 90-second story (~225 words)
    4. Create a JSON array with format: [{"location_name": "Name", "story": "Your story text..."}, ...]
    5. Use generate_and_save_stories_tool(tour_id, stories_json) to save all stories
    6. Respond with a summary of what was done

    IMPORTANT: Generate actual creative stories, not placeholders. Each story should be unique and specific to that location.
    """,

    description="Generates engaging 90-second narratives for tour locations using Gemini 2.0 Flash",

    # Tools available to this agent
    tools=[
        get_tour_tool,
        generate_and_save_stories_tool,
        publish_to_moderator_tool
    ]
)


# Export for deployment
agent = storytelling_agent

if __name__ == "__main__":
    # For local testing
    print(f"Storytelling Agent initialized: {agent.name}")
    print(f"Model: {agent.model}")
    print(f"Tools: {len(agent.tools)}")
