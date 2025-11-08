"""
Tour Curator Agent - Personalizes tour routes based on user preferences

This agent:
1. Analyzes user preferences (interests, duration, accessibility)
2. Queries location database from Firestore
3. Selects optimal points of interest
4. Creates personalized 30-minute walking routes
5. Publishes results to Pub/Sub for Route Optimizer Agent
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


class TourCuratorAgent:
    """Agent that curates personalized tour routes"""

    def __init__(self):
        self.name = "tour-curator-agent"
        self.version = "1.0.0"

    def analyze_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to analyze user preferences and extract key requirements

        Args:
            preferences: User preferences dict with interests, duration, etc.

        Returns:
            Analyzed preferences with weighted categories
        """
        try:
            if not model:
                # Mock response for development
                return {
                    "primary_interests": preferences.get("interests", ["history"]),
                    "secondary_interests": ["architecture", "culture"],
                    "duration_minutes": preferences.get("duration", 30),
                    "difficulty_level": "easy",
                    "accessibility_needs": preferences.get("accessibility", [])
                }

            prompt = f"""
            Analyze these tour preferences and extract key requirements:

            User Input:
            {json.dumps(preferences, indent=2)}

            Provide a JSON response with:
            1. primary_interests: Main categories to focus on (max 2)
            2. secondary_interests: Additional nice-to-have categories
            3. duration_minutes: Ideal tour duration
            4. difficulty_level: easy/moderate/challenging
            5. accessibility_needs: Any special requirements

            Keep the response concise and actionable for location selection.
            """

            response = model.generate_content(prompt)

            # Parse Gemini response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            analyzed = json.loads(text)
            logger.info(f"Analyzed preferences: {analyzed}")
            return analyzed

        except Exception as e:
            logger.error(f"Error analyzing preferences: {e}")
            # Fallback to simple analysis
            return {
                "primary_interests": preferences.get("interests", ["history"]),
                "secondary_interests": [],
                "duration_minutes": preferences.get("duration", 30),
                "difficulty_level": "easy",
                "accessibility_needs": preferences.get("accessibility", [])
            }

    def query_locations(self, analyzed_prefs: Dict[str, Any], start_location: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Query Firestore for locations matching preferences

        Args:
            analyzed_prefs: Analyzed user preferences
            start_location: Starting point {lat, lng}

        Returns:
            List of matching locations
        """
        try:
            locations_ref = firestore_client.collection('locations')

            # Query by primary interests
            primary_interests = analyzed_prefs.get("primary_interests", ["history"])

            # For MVP, get all locations and filter in memory
            # In production, use composite indexes
            all_locations = locations_ref.limit(100).stream()

            matching_locations = []
            for doc in all_locations:
                location = doc.to_dict()
                location['id'] = doc.id

                # Check if location matches interests
                location_categories = location.get('categories', [])
                if any(interest in location_categories for interest in primary_interests):
                    matching_locations.append(location)

            logger.info(f"Found {len(matching_locations)} matching locations")
            return matching_locations

        except Exception as e:
            logger.error(f"Error querying locations: {e}")
            # Return mock locations for development
            return self._get_mock_locations()

    def _get_mock_locations(self) -> List[Dict[str, Any]]:
        """Mock locations for development"""
        return [
            {
                "id": "loc_001",
                "name": "Historic City Hall",
                "categories": ["history", "architecture"],
                "coordinates": {"lat": 40.7128, "lng": -74.0060},
                "description": "Built in 1803, this neoclassical building...",
                "average_visit_minutes": 5,
                "accessibility": ["wheelchair_accessible", "elevator"]
            },
            {
                "id": "loc_002",
                "name": "Hidden Alleyway Mural",
                "categories": ["art", "hidden gems"],
                "coordinates": {"lat": 40.7138, "lng": -74.0050},
                "description": "Local artist's 90s tribute to the neighborhood...",
                "average_visit_minutes": 3,
                "accessibility": ["wheelchair_accessible"]
            },
            {
                "id": "loc_003",
                "name": "Artisan Coffee House",
                "categories": ["food", "local culture"],
                "coordinates": {"lat": 40.7148, "lng": -74.0040},
                "description": "Family-owned since 1950...",
                "average_visit_minutes": 4,
                "accessibility": ["wheelchair_accessible", "restroom"]
            },
            {
                "id": "loc_004",
                "name": "Revolutionary War Monument",
                "categories": ["history", "outdoor"],
                "coordinates": {"lat": 40.7158, "lng": -74.0030},
                "description": "Commemorates the 1776 battle...",
                "average_visit_minutes": 4,
                "accessibility": ["wheelchair_accessible"]
            },
            {
                "id": "loc_005",
                "name": "Street Art Gallery Walk",
                "categories": ["art", "outdoor"],
                "coordinates": {"lat": 40.7168, "lng": -74.0020},
                "description": "Open-air gallery featuring local artists...",
                "average_visit_minutes": 5,
                "accessibility": ["wheelchair_accessible"]
            },
            {
                "id": "loc_006",
                "name": "Historic Market Square",
                "categories": ["history", "food", "local culture"],
                "coordinates": {"lat": 40.7178, "lng": -74.0010},
                "description": "Operating since 1812, this farmers market...",
                "average_visit_minutes": 6,
                "accessibility": ["wheelchair_accessible", "seating"]
            }
        ]

    def select_locations(self, locations: List[Dict[str, Any]], analyzed_prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select optimal locations based on preferences and duration

        Args:
            locations: Available locations
            analyzed_prefs: Analyzed preferences

        Returns:
            Selected locations for the tour
        """
        duration_minutes = analyzed_prefs.get("duration_minutes", 30)

        # Reserve 40% of time for walking, 60% for stories
        available_story_time = duration_minutes * 0.6

        selected = []
        total_time = 0

        # Sort by relevance (locations matching primary interests first)
        primary_interests = analyzed_prefs.get("primary_interests", [])

        def relevance_score(loc):
            categories = loc.get('categories', [])
            score = sum(2 if cat in primary_interests else 1 for cat in categories)
            return score

        sorted_locations = sorted(locations, key=relevance_score, reverse=True)

        # Select locations until we fill the time
        for location in sorted_locations:
            visit_time = location.get('average_visit_minutes', 5)

            if total_time + visit_time <= available_story_time:
                selected.append(location)
                total_time += visit_time

            # Aim for 5-8 stops
            if len(selected) >= 8:
                break

        logger.info(f"Selected {len(selected)} locations, total story time: {total_time} minutes")
        return selected

    def create_tour_structure(self, selected_locations: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create initial tour structure

        Args:
            selected_locations: Selected locations
            preferences: Original user preferences

        Returns:
            Tour structure ready for route optimization
        """
        tour_id = f"tour_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}"

        tour = {
            "tour_id": tour_id,
            "status": "route_planning",
            "created_at": datetime.now().isoformat(),
            "preferences": preferences,
            "locations": selected_locations,
            "estimated_stops": len(selected_locations),
            "estimated_story_time": sum(loc.get('average_visit_minutes', 5) for loc in selected_locations),
            "agent_version": self.version
        }

        return tour

    def publish_to_optimizer(self, tour: Dict[str, Any]):
        """
        Publish tour to Route Optimizer Agent via Pub/Sub

        Args:
            tour: Tour structure to optimize
        """
        try:
            topic_path = publisher.topic_path(PROJECT_ID, 'route-planned')

            message_data = json.dumps(tour).encode('utf-8')
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()

            logger.info(f"Published tour {tour['tour_id']} to route-planned: {message_id}")

        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {e}")
            # For development, continue without Pub/Sub

    def curate_tour(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to curate a personalized tour

        Args:
            request_data: User request with preferences

        Returns:
            Curated tour structure
        """
        logger.info(f"Curating tour with preferences: {request_data}")

        # Step 1: Analyze preferences with Gemini
        analyzed_prefs = self.analyze_preferences(request_data.get('preferences', {}))

        # Step 2: Query matching locations from Firestore
        start_location = request_data.get('start_location', {"lat": 40.7128, "lng": -74.0060})
        locations = self.query_locations(analyzed_prefs, start_location)

        # Step 3: Select optimal locations
        selected_locations = self.select_locations(locations, analyzed_prefs)

        # Step 4: Create tour structure
        tour = self.create_tour_structure(selected_locations, request_data.get('preferences', {}))

        # Step 5: Publish to Route Optimizer Agent
        self.publish_to_optimizer(tour)

        return tour


# Initialize agent
agent = TourCuratorAgent()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "tour-curator-agent",
        "version": agent.version
    })


@app.route('/curate', methods=['POST'])
def curate_tour():
    """
    Curate a personalized tour

    Request body:
    {
        "preferences": {
            "interests": ["history", "art"],
            "duration": 30,
            "accessibility": ["wheelchair_accessible"]
        },
        "start_location": {
            "lat": 40.7128,
            "lng": -74.0060
        }
    }
    """
    try:
        request_data = request.get_json()

        if not request_data:
            return jsonify({"error": "Request body required"}), 400

        # Curate the tour
        tour = agent.curate_tour(request_data)

        return jsonify({
            "success": True,
            "tour": tour,
            "message": "Tour curated successfully. Route optimization in progress."
        })

    except Exception as e:
        logger.error(f"Error in curate_tour: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/pubsub', methods=['POST'])
def pubsub_push():
    """
    Handle Pub/Sub push messages
    (For future use if this agent needs to respond to events)
    """
    envelope = request.get_json()

    if not envelope:
        return "Bad Request: no Pub/Sub message received", 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        return "Bad Request: invalid Pub/Sub message format", 400

    # Process message (implement as needed)
    logger.info(f"Received Pub/Sub message: {envelope}")

    return "OK", 200


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
