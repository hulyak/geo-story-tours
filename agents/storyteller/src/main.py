"""
Storytelling Agent - Generates engaging 90-second narratives using Gemini

This agent:
1. Receives optimized tour routes from Route Optimizer
2. Uses Gemini 2.0 Flash to generate compelling 90-second stories
3. Adapts tone based on audience (family-friendly, historical, local secrets)
4. Creates scripts that blend facts with emotional storytelling
5. Publishes completed stories to Content Moderator Agent
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

from flask import Flask, request, jsonify
from google.cloud import firestore, pubsub_v1
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()

# Initialize Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    logger.warning("GEMINI_API_KEY not set, using mock responses")
    model = None


class StorytellingAgent:
    """Agent that generates engaging 90-second narratives"""

    def __init__(self):
        self.name = "storytelling-agent"
        self.version = "1.0.0"
        self.target_duration_seconds = 90
        self.words_per_second = 2.5  # Average speaking pace

    def generate_story(self, location: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a captivating 90-second narrative for a location using Gemini

        Args:
            location: Location data with name, description, categories
            context: Additional context (audience type, previous locations, tour theme)

        Returns:
            Story dict with script, duration estimate, tone
        """
        try:
            if not model:
                # Mock response for development
                return self._generate_mock_story(location, context)

            # Calculate target word count (90 seconds * 2.5 words/second = ~225 words)
            target_words = int(self.target_duration_seconds * self.words_per_second)

            audience = context.get('audience', 'general')
            tour_theme = context.get('tour_theme', 'discovery')
            previous_locations = context.get('previous_locations', [])

            # Build context from previous locations
            context_str = ""
            if previous_locations:
                context_str = f"\nPrevious stops on this tour: {', '.join(prev['name'] for prev in previous_locations[-2:])}"

            prompt = f"""
            You are a masterful storyteller creating a micro-tour narrative. Generate a captivating {self.target_duration_seconds}-second story for this location.

            Location Details:
            - Name: {location.get('name')}
            - Description: {location.get('description')}
            - Categories: {', '.join(location.get('categories', []))}
            - Historical Context: {location.get('historical_context', 'Local landmark')}
            {context_str}

            Requirements:
            1. Target length: approximately {target_words} words ({self.target_duration_seconds} seconds when read aloud)
            2. Audience: {audience} (adapt tone accordingly)
            3. Theme: {tour_theme}
            4. Structure:
               - Opening hook (5-10 seconds): Grab attention immediately
               - Story body (70-75 seconds): Blend historical facts with emotional storytelling
               - Closing (5-10 seconds): Connect to the present or next location

            Guidelines:
            - Use vivid, sensory language ("imagine", "picture this", "you can almost hear")
            - Include surprising facts or little-known details
            - Make it personal and relatable
            - Avoid clichés like "nestled" or "hidden gem"
            - Use present tense to create immediacy
            - End with a thought-provoking question or observation

            Tone Guidelines by Audience:
            - family-friendly: Engaging, wonder-filled, educational but fun
            - historical: Scholarly but accessible, rich in detail
            - local-secrets: Conspiratorial, insider knowledge, off-the-beaten-path
            - general: Balanced, universally appealing, conversational

            Generate ONLY the story script. No preamble, no metadata. Just the narrative ready to be read aloud.
            """

            response = model.generate_content(prompt)
            script = response.text.strip()

            # Estimate actual duration based on word count
            word_count = len(script.split())
            estimated_duration = int(word_count / self.words_per_second)

            logger.info(f"Generated story for {location.get('name')}: {word_count} words, ~{estimated_duration}s")

            # If duration is significantly off target, regenerate with adjustment
            if abs(estimated_duration - self.target_duration_seconds) > 15:
                logger.warning(f"Story duration off target ({estimated_duration}s vs {self.target_duration_seconds}s), adjusting...")
                script = self._adjust_story_length(script, estimated_duration, context)
                word_count = len(script.split())
                estimated_duration = int(word_count / self.words_per_second)

            return {
                "script": script,
                "word_count": word_count,
                "estimated_duration_seconds": estimated_duration,
                "tone": audience,
                "generated_at": datetime.now().isoformat(),
                "model_version": "gemini-2.5-flash"
            }

        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return self._generate_mock_story(location, context)

    def _adjust_story_length(self, script: str, current_duration: int, context: Dict[str, Any]) -> str:
        """
        Adjust story length if it's significantly off target

        Args:
            script: Current script
            current_duration: Current estimated duration
            context: Story context

        Returns:
            Adjusted script
        """
        try:
            if not model:
                return script

            if current_duration > self.target_duration_seconds:
                instruction = f"Shorten this to {self.target_duration_seconds} seconds while keeping the most compelling parts"
            else:
                instruction = f"Expand this to {self.target_duration_seconds} seconds with more vivid details and sensory language"

            prompt = f"""
            {instruction}:

            {script}

            Maintain the same tone and style. Keep the hook and closing intact if possible.
            """

            response = model.generate_content(prompt)
            adjusted_script = response.text.strip()

            logger.info(f"Adjusted story length: {len(script.split())} -> {len(adjusted_script.split())} words")
            return adjusted_script

        except Exception as e:
            logger.error(f"Error adjusting story length: {e}")
            return script

    def _generate_mock_story(self, location: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock story for development/testing"""

        mock_script = f"""
        Stop here. Right here. Do you feel it?

        {location.get('name')} isn't just another spot on the map. In 1823, this exact corner changed everything.
        Picture Maria Santos, a 16-year-old who stood here with a decision that would reshape the neighborhood.
        The cobblestones beneath your feet? They heard her footsteps as she walked toward the unknown.

        Look up. That second-floor window? That's where she watched for the signal.
        The brick pattern—see how it changes halfway up? That's from the fire of 1847.
        People rebuilt. They always do.

        Today, locals still leave coins in that crack over there. Not for luck. For memory.
        Because every place has a story. And some stories refuse to be forgotten.

        What would you have done in Maria's place?
        """

        return {
            "script": mock_script.strip(),
            "word_count": len(mock_script.split()),
            "estimated_duration_seconds": 85,
            "tone": context.get('audience', 'general'),
            "generated_at": datetime.now().isoformat(),
            "model_version": "mock"
        }

    def generate_tour_stories(self, tour_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate stories for all locations in a tour

        Args:
            tour_data: Complete tour data with route from Route Optimizer

        Returns:
            Updated tour with generated stories
        """
        logger.info(f"Generating stories for tour {tour_data.get('tour_id')}")

        locations = tour_data.get('locations', [])
        audience = tour_data.get('preferences', {}).get('audience', 'general')
        tour_theme = self._determine_tour_theme(tour_data.get('preferences', {}))

        stories = []
        previous_locations = []

        for i, location in enumerate(locations):
            logger.info(f"Generating story {i+1}/{len(locations)}: {location.get('name')}")

            context = {
                "audience": audience,
                "tour_theme": tour_theme,
                "previous_locations": previous_locations,
                "stop_number": i + 1,
                "total_stops": len(locations)
            }

            story = self.generate_story(location, context)

            # Attach story to location
            location['story'] = story
            stories.append(story)

            previous_locations.append(location)

        # Update tour data
        tour_data['stories'] = stories
        tour_data['status'] = 'stories_generated'
        tour_data['storytelling_completed_at'] = datetime.now().isoformat()

        # Calculate total tour duration
        total_duration = sum(story['estimated_duration_seconds'] for story in stories)
        tour_data['total_story_duration_seconds'] = total_duration

        logger.info(f"Generated {len(stories)} stories, total duration: {total_duration}s")

        return tour_data

    def _determine_tour_theme(self, preferences: Dict[str, Any]) -> str:
        """Determine the overarching theme of the tour"""
        interests = preferences.get('interests', [])

        theme_map = {
            ('history', 'architecture'): 'architectural-heritage',
            ('art', 'culture'): 'creative-exploration',
            ('food', 'local'): 'culinary-journey',
            ('hidden', 'gems'): 'secret-discovery',
            ('nature', 'outdoor'): 'urban-nature'
        }

        for key, theme in theme_map.items():
            if any(interest in interests for interest in key):
                return theme

        return 'urban-discovery'

    def save_to_firestore(self, tour_data: Dict[str, Any]):
        """
        Save tour with stories to Firestore

        Args:
            tour_data: Complete tour data
        """
        try:
            tour_id = tour_data.get('tour_id')
            tours_ref = firestore_client.collection('tours')

            tours_ref.document(tour_id).set(tour_data)

            logger.info(f"Saved tour {tour_id} to Firestore")

        except Exception as e:
            logger.error(f"Error saving to Firestore: {e}")

    def publish_to_moderator(self, tour_data: Dict[str, Any]):
        """
        Publish tour to Content Moderator Agent via Pub/Sub

        Args:
            tour_data: Tour with generated stories
        """
        try:
            topic_path = publisher.topic_path(PROJECT_ID, 'stories-generated')

            message_data = json.dumps(tour_data).encode('utf-8')
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()

            logger.info(f"Published tour {tour_data['tour_id']} to stories-generated: {message_id}")

        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {e}")
            # For development, continue without Pub/Sub


# Initialize agent
agent = StorytellingAgent()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "storytelling-agent",
        "version": agent.version,
        "gemini_configured": model is not None
    })


@app.route('/generate-story', methods=['POST'])
def generate_single_story():
    """
    Generate a single story for a location

    Request body:
    {
        "location": {
            "name": "Historic City Hall",
            "description": "Built in 1803...",
            "categories": ["history", "architecture"]
        },
        "context": {
            "audience": "family-friendly",
            "tour_theme": "architectural-heritage"
        }
    }
    """
    try:
        request_data = request.get_json()

        if not request_data or 'location' not in request_data:
            return jsonify({"error": "Location data required"}), 400

        location = request_data['location']
        context = request_data.get('context', {})

        # Generate story
        story = agent.generate_story(location, context)

        return jsonify({
            "success": True,
            "story": story
        })

    except Exception as e:
        logger.error(f"Error in generate_single_story: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/generate-tour-stories', methods=['POST'])
def generate_tour_stories_endpoint():
    """
    Generate stories for an entire tour

    Request body:
    {
        "tour_id": "tour_123",
        "locations": [...],
        "preferences": {...}
    }
    """
    try:
        tour_data = request.get_json()

        if not tour_data:
            return jsonify({"error": "Tour data required"}), 400

        # Generate all stories
        updated_tour = agent.generate_tour_stories(tour_data)

        # Save to Firestore
        agent.save_to_firestore(updated_tour)

        # Publish to Content Moderator
        agent.publish_to_moderator(updated_tour)

        return jsonify({
            "success": True,
            "tour": updated_tour,
            "message": f"Generated {len(updated_tour.get('stories', []))} stories. Content moderation in progress."
        })

    except Exception as e:
        logger.error(f"Error in generate_tour_stories: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/pubsub', methods=['POST'])
def pubsub_push():
    """
    Handle Pub/Sub push messages from Route Optimizer
    """
    envelope = request.get_json()

    if not envelope:
        return "Bad Request: no Pub/Sub message received", 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        return "Bad Request: invalid Pub/Sub message format", 400

    try:
        # Decode Pub/Sub message
        import base64
        message_data = json.loads(base64.b64decode(envelope['message']['data']))

        logger.info(f"Received Pub/Sub message for tour: {message_data.get('tour_id')}")

        # Generate stories for the tour
        updated_tour = agent.generate_tour_stories(message_data)

        # Save and publish
        agent.save_to_firestore(updated_tour)
        agent.publish_to_moderator(updated_tour)

        return "OK", 200

    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True)
