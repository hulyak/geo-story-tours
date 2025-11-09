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


def generate_story_tool(location: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Tool for generating 90-second stories for locations.

    This tool is called by the ADK agent when it needs to create stories.

    Args:
        location: Location data with name, description, categories
        context: Additional context (audience type, tour theme)

    Returns:
        Generated story script
    """
    # Story generation logic (reusing our sophisticated logic)
    target_duration_seconds = 90
    words_per_second = 2.5
    target_words = int(target_duration_seconds * words_per_second)

    audience = context.get('audience', 'general')
    tour_theme = context.get('tour_theme', 'discovery')

    # The agent's LLM will actually generate the content based on our instruction
    # We just need to format the response
    return f"Tool executed for {location.get('name')}"


def save_to_firestore_tool(tour_id: str, tour_data: Dict[str, Any]) -> str:
    """
    Tool for saving tour data to Firestore.

    Args:
        tour_id: Tour identifier
        tour_data: Complete tour data

    Returns:
        Success message
    """
    try:
        tours_ref = firestore_client.collection('tours')
        tours_ref.document(tour_id).set(tour_data)
        return f"Successfully saved tour {tour_id} to Firestore"
    except Exception as e:
        return f"Error saving to Firestore: {e}"


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

    When you receive a tour with locations, generate a story for each location,
    save the tour to Firestore, and publish it to the Content Moderator.
    """,

    description="Generates engaging 90-second narratives for tour locations using Gemini 2.0 Flash",

    # Tools available to this agent
    tools=[
        generate_story_tool,
        save_to_firestore_tool,
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
