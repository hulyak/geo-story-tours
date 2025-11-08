"""
Content Moderator Agent - Google ADK Implementation

Validates quality and appropriateness of generated tour content.
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore
import os
import json
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)


def moderate_story_tool(story_text: str, location_name: str) -> str:
    """
    Evaluate a story for quality, safety, and appropriateness.

    This tool uses the agent's own Gemini model to assess the story.

    Args:
        story_text: The story script to moderate
        location_name: Name of the location

    Returns:
        JSON moderation result with approval status
    """
    # The LLM will perform the actual moderation based on the instruction
    # This tool just structures the request
    return json.dumps({
        "story_text": story_text,
        "location_name": location_name,
        "requires_moderation": True
    })


def update_tour_status_tool(tour_id: str, status: str, moderation_results: List[Dict]) -> str:
    """
    Update tour with moderation results and final status.

    Args:
        tour_id: Tour identifier
        status: Final status ("approved" or "requires_review")
        moderation_results: List of moderation results for each story

    Returns:
        Success message
    """
    try:
        tours_ref = firestore_client.collection('tours')
        tours_ref.document(tour_id).update({
            "status": status,
            "moderation_completed_at": datetime.now().isoformat(),
            "moderation_results": moderation_results,
            "approved_at": datetime.now().isoformat() if status == "approved" else None
        })

        return f"Tour {tour_id} updated with status: {status}"

    except Exception as e:
        return f"Error: {str(e)}"


# Define the Content Moderator Agent using Google ADK
moderator_agent = Agent(
    name="content_moderator_agent",
    model="gemini-2.0-flash-exp",

    instruction="""
    You are the Content Moderator Agent for Geo-Story Micro-Tours.

    Your job is to ensure all tour content is high-quality, safe, and appropriate.

    When you receive a tour with generated stories, you should:
    1. Review each story for the following criteria:
       - Content Safety: Appropriate for all audiences
       - Factual Accuracy: Historical/cultural facts are plausible
       - Quality: Engaging and well-written
       - Length: Appropriate for 90-second audio
       - Tone: Respectful and appropriate

    2. For each story, provide:
       - approved: true/false
       - safety_score: 0-100
       - quality_score: 0-100
       - issues: List of any concerns
       - suggestions: List of improvements
       - reasoning: Brief explanation

    3. Use update_tour_status_tool to set final status:
       - "approved" if all stories pass
       - "requires_review" if any story has issues

    Be thorough but fair. Most well-written stories should pass.
    Only flag content that is clearly inappropriate, inaccurate, or low-quality.

    Provide a summary of your moderation including:
    - Number of stories reviewed
    - Number approved
    - Overall quality assessment
    - Any concerns flagged
    """,

    description="Reviews tour content for quality, safety, and factual accuracy",

    tools=[
        moderate_story_tool,
        update_tour_status_tool
    ]
)


# Export for deployment
agent = moderator_agent

if __name__ == "__main__":
    print(f"✅ Content Moderator Agent initialized: {agent.name}")
    print(f"📦 Model: {agent.model}")
    print(f"🔧 Tools: {len(agent.tools)}")
