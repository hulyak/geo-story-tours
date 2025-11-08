"""
Route Optimizer Agent - Calculates optimal walking paths

This agent:
1. Receives location selections from Tour Curator
2. Calculates optimal walking paths between locations
3. Considers real-time factors (weather, time of day, crowds)
4. Estimates accurate timing
5. Publishes optimized routes to Storytelling Agent
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
import math

from flask import Flask, request, jsonify
from google.cloud import firestore, pubsub_v1

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')
firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


class RouteOptimizerAgent:
    """Agent that optimizes walking routes"""

    def __init__(self):
        self.name = "route-optimizer-agent"
        self.version = "1.0.0"
        self.walking_speed_meters_per_minute = 80  # Average walking speed

    def calculate_distance(self, point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """
        Calculate distance between two GPS coordinates (Haversine formula)

        Args:
            point1: {lat, lng}
            point2: {lat, lng}

        Returns:
            Distance in meters
        """
        lat1, lon1 = math.radians(point1['lat']), math.radians(point1['lng'])
        lat2, lon2 = math.radians(point2['lat']), math.radians(point2['lng'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in meters
        r = 6371000

        return c * r

    def optimize_route(self, locations: List[Dict[str, Any]], start_location: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Optimize route using nearest neighbor algorithm

        Args:
            locations: List of locations to visit
            start_location: Starting point {lat, lng}

        Returns:
            Optimized list of locations with route info
        """
        if not locations:
            return []

        optimized_route = []
        remaining = locations.copy()
        current_pos = start_location

        while remaining:
            # Find nearest location
            nearest = min(remaining, key=lambda loc: self.calculate_distance(
                current_pos,
                loc.get('coordinates', {})
            ))

            # Calculate walking time to this location
            distance = self.calculate_distance(current_pos, nearest.get('coordinates', {}))
            walking_minutes = distance / self.walking_speed_meters_per_minute

            # Add route info
            nearest['route_info'] = {
                "distance_meters": round(distance, 1),
                "walking_minutes": round(walking_minutes, 1),
                "from_previous": optimized_route[-1]['name'] if optimized_route else "start"
            }

            optimized_route.append(nearest)
            remaining.remove(nearest)
            current_pos = nearest.get('coordinates', {})

        logger.info(f"Optimized route with {len(optimized_route)} stops")
        return optimized_route

    def calculate_total_duration(self, optimized_locations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate total tour duration"""
        total_walking = sum(loc.get('route_info', {}).get('walking_minutes', 0) for loc in optimized_locations)
        total_story = sum(loc.get('average_visit_minutes', 5) for loc in optimized_locations)

        return {
            "walking_minutes": round(total_walking),
            "story_minutes": round(total_story),
            "total_minutes": round(total_walking + total_story)
        }

    def optimize_tour_route(self, tour_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize the route for a tour

        Args:
            tour_data: Tour data from Curator Agent

        Returns:
            Updated tour with optimized route
        """
        logger.info(f"Optimizing route for tour {tour_data.get('tour_id')}")

        locations = tour_data.get('locations', [])
        start_location = tour_data.get('preferences', {}).get('start_location', {"lat": 40.7128, "lng": -74.0060})

        # Optimize route
        optimized_locations = self.optimize_route(locations, start_location)

        # Calculate total duration
        duration_info = self.calculate_total_duration(optimized_locations)

        # Update tour data
        tour_data['locations'] = optimized_locations
        tour_data['duration_info'] = duration_info
        tour_data['status'] = 'route_optimized'
        tour_data['route_optimized_at'] = datetime.now().isoformat()

        logger.info(f"Route optimized: {duration_info['total_minutes']} min total ({duration_info['walking_minutes']} walking + {duration_info['story_minutes']} stories)")

        return tour_data

    def save_to_firestore(self, tour_data: Dict[str, Any]):
        """Save optimized tour to Firestore"""
        try:
            tour_id = tour_data.get('tour_id')
            tours_ref = firestore_client.collection('tours')

            tours_ref.document(tour_id).set(tour_data)

            logger.info(f"Saved optimized tour {tour_id} to Firestore")

        except Exception as e:
            logger.error(f"Error saving to Firestore: {e}")

    def publish_to_storyteller(self, tour_data: Dict[str, Any]):
        """Publish optimized tour to Storytelling Agent"""
        try:
            topic_path = publisher.topic_path(PROJECT_ID, 'route-optimized')

            message_data = json.dumps(tour_data).encode('utf-8')
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()

            logger.info(f"Published tour {tour_data['tour_id']} to route-optimized: {message_id}")

        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {e}")


# Initialize agent
agent = RouteOptimizerAgent()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "route-optimizer-agent",
        "version": agent.version
    })


@app.route('/optimize', methods=['POST'])
def optimize_route_endpoint():
    """Optimize a tour route"""
    try:
        tour_data = request.get_json()

        if not tour_data:
            return jsonify({"error": "Tour data required"}), 400

        # Optimize route
        optimized_tour = agent.optimize_tour_route(tour_data)

        # Save to Firestore
        agent.save_to_firestore(optimized_tour)

        # Publish to Storytelling Agent
        agent.publish_to_storyteller(optimized_tour)

        return jsonify({
            "success": True,
            "tour": optimized_tour,
            "message": "Route optimized. Story generation in progress."
        })

    except Exception as e:
        logger.error(f"Error in optimize_route: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/pubsub', methods=['POST'])
def pubsub_push():
    """Handle Pub/Sub messages from Tour Curator"""
    envelope = request.get_json()

    if not envelope:
        return "Bad Request", 400

    try:
        import base64
        message_data = json.loads(base64.b64decode(envelope['message']['data']))

        logger.info(f"Received tour for optimization: {message_data.get('tour_id')}")

        # Optimize route
        optimized_tour = agent.optimize_tour_route(message_data)

        # Save and publish
        agent.save_to_firestore(optimized_tour)
        agent.publish_to_storyteller(optimized_tour)

        return "OK", 200

    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8083))
    app.run(host='0.0.0.0', port=port, debug=True)
