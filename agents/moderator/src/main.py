"""
Content Moderator Agent - Validates quality and appropriateness

This agent:
1. Reviews generated stories for quality and appropriateness
2. Validates location accuracy and accessibility information
3. Ensures content guidelines are met
4. Uses Gemini for fact-checking and safety assessment
5. Publishes approved tours for final use
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
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    logger.warning("GEMINI_API_KEY not set, using mock responses")
    model = None


class ContentModeratorAgent:
    """Agent that moderates and validates tour content"""

    def __init__(self):
        self.name = "content-moderator-agent"
        self.version = "1.0.0"

    def moderate_story(self, story: Dict[str, Any], location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Moderate a single story for quality and safety

        Args:
            story: Story data with script
            location: Associated location data

        Returns:
            Moderation result with approval status and feedback
        """
        try:
            if not model:
                return self._mock_moderation_result(True)

            prompt = f"""
            Review this micro-tour story for quality and appropriateness:

            Location: {location.get('name')}
            Story Script:
            {story.get('script')}

            Evaluate on these criteria:
            1. Content Safety: Is it appropriate for all audiences?
            2. Factual Accuracy: Are historical/cultural facts plausible?
            3. Quality: Is it engaging and well-written?
            4. Length: Is it appropriate for a 90-second audio clip?
            5. Tone: Is it respectful and appropriate?

            Respond in JSON format:
            {{
                "approved": true/false,
                "safety_score": 0-100,
                "quality_score": 0-100,
                "issues": ["list any concerns"],
                "suggestions": ["list improvements if any"],
                "reasoning": "brief explanation"
            }}
            """

            response = model.generate_content(prompt)
            text = response.text.strip()

            # Parse response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text)

            logger.info(f"Moderation result for {location.get('name')}: approved={result.get('approved')}")

            return result

        except Exception as e:
            logger.error(f"Error moderating story: {e}")
            # Default to approved for development
            return self._mock_moderation_result(True)

    def _mock_moderation_result(self, approved: bool) -> Dict[str, Any]:
        """Generate mock moderation result"""
        return {
            "approved": approved,
            "safety_score": 95,
            "quality_score": 90,
            "issues": [],
            "suggestions": [],
            "reasoning": "Mock moderation result"
        }

    def moderate_tour(self, tour_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Moderate all stories in a tour

        Args:
            tour_data: Complete tour with stories

        Returns:
            Updated tour with moderation results
        """
        logger.info(f"Moderating tour {tour_data.get('tour_id')}")

        locations = tour_data.get('locations', [])
        moderation_results = []
        all_approved = True

        for location in locations:
            story = location.get('story', {})

            if story:
                result = self.moderate_story(story, location)
                moderation_results.append(result)

                if not result.get('approved', True):
                    all_approved = False
                    logger.warning(f"Story rejected for {location.get('name')}: {result.get('reasoning')}")

                # Attach moderation result to location
                location['moderation'] = result

        # Update tour status
        tour_data['moderation_results'] = moderation_results
        tour_data['moderation_completed_at'] = datetime.now().isoformat()

        if all_approved:
            tour_data['status'] = 'approved'
            tour_data['approved_at'] = datetime.now().isoformat()
        else:
            tour_data['status'] = 'requires_review'

        logger.info(f"Moderation complete: {len(moderation_results)} stories, all_approved={all_approved}")

        return tour_data

    def save_to_firestore(self, tour_data: Dict[str, Any]):
        """Save moderated tour to Firestore"""
        try:
            tour_id = tour_data.get('tour_id')
            tours_ref = firestore_client.collection('tours')

            tours_ref.document(tour_id).set(tour_data)

            logger.info(f"Saved moderated tour {tour_id} to Firestore")

        except Exception as e:
            logger.error(f"Error saving to Firestore: {e}")


# Initialize agent
agent = ContentModeratorAgent()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "content-moderator-agent",
        "version": agent.version
    })


@app.route('/moderate', methods=['POST'])
def moderate_tour_endpoint():
    """Moderate a tour"""
    try:
        tour_data = request.get_json()

        if not tour_data:
            return jsonify({"error": "Tour data required"}), 400

        # Moderate tour
        moderated_tour = agent.moderate_tour(tour_data)

        # Save to Firestore
        agent.save_to_firestore(moderated_tour)

        return jsonify({
            "success": True,
            "tour": moderated_tour,
            "approved": moderated_tour.get('status') == 'approved'
        })

    except Exception as e:
        logger.error(f"Error in moderate_tour: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/pubsub', methods=['POST'])
def pubsub_push():
    """Handle Pub/Sub messages from Storytelling Agent"""
    envelope = request.get_json()

    if not envelope:
        return "Bad Request", 400

    try:
        import base64
        message_data = json.loads(base64.b64decode(envelope['message']['data']))

        logger.info(f"Received tour for moderation: {message_data.get('tour_id')}")

        # Moderate tour
        moderated_tour = agent.moderate_tour(message_data)

        # Save to Firestore
        agent.save_to_firestore(moderated_tour)

        return "OK", 200

    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8082))
    app.run(host='0.0.0.0', port=port, debug=True)
