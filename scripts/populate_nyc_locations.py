#!/usr/bin/env python3
"""
Populate Firestore with New York City locations for tours.
"""

from google.cloud import firestore
import os

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# New York City locations
NYC_LOCATIONS = [
    {
        "id": "statue_of_liberty",
        "name": "Statue of Liberty",
        "address": "Liberty Island, New York, NY 10004",
        "description": "Iconic symbol of freedom and democracy",
        "categories": ["history", "landmarks", "monuments"],
        "lat": 40.6892,
        "lng": -74.0445,
        "duration": 20,
        "image_url": "https://images.unsplash.com/photo-1566404791232-af9fe0ae8f8b?w=1200&q=80"
    },
    {
        "id": "central_park",
        "name": "Central Park",
        "address": "Central Park, New York, NY 10024",
        "description": "Massive urban park with lakes, gardens, and trails",
        "categories": ["parks", "nature", "relaxation"],
        "lat": 40.7829,
        "lng": -73.9654,
        "duration": 30,
        "image_url": "https://images.unsplash.com/photo-1568515387631-8b650bbcdb90?w=1200&q=80"
    },
    {
        "id": "empire_state_building",
        "name": "Empire State Building",
        "address": "20 W 34th St, New York, NY 10001",
        "description": "Art Deco skyscraper with iconic city views",
        "categories": ["landmarks", "architecture", "viewpoints"],
        "lat": 40.7484,
        "lng": -73.9857,
        "duration": 15,
        "image_url": "https://images.unsplash.com/photo-1564659172-5881935e1fcc?w=1200&q=80"
    },
    {
        "id": "times_square",
        "name": "Times Square",
        "address": "Times Square, Manhattan, NY 10036",
        "description": "Vibrant intersection with neon signs and Broadway theaters",
        "categories": ["entertainment", "landmarks", "nightlife"],
        "lat": 40.758,
        "lng": -73.9855,
        "duration": 15,
        "image_url": "https://images.unsplash.com/photo-1564221710304-0b37c8b9d729?w=1200&q=80"
    },
    {
        "id": "brooklyn_bridge",
        "name": "Brooklyn Bridge",
        "address": "Brooklyn Bridge, New York, NY 10038",
        "description": "Historic suspension bridge connecting Manhattan and Brooklyn",
        "categories": ["landmarks", "architecture", "history"],
        "lat": 40.7061,
        "lng": -73.9969,
        "duration": 20,
        "image_url": "https://images.unsplash.com/photo-1541336032412-2048ef1039e5?w=1200&q=80"
    },
    {
        "id": "metropolitan_museum",
        "name": "Metropolitan Museum of Art",
        "address": "1000 5th Ave, New York, NY 10028",
        "description": "World-renowned art museum with vast collections",
        "categories": ["art", "museums", "culture"],
        "lat": 40.7794,
        "lng": -73.9632,
        "duration": 25,
        "image_url": "https://images.unsplash.com/photo-1560552958-6d4f302f7e04?w=1200&q=80"
    },
    {
        "id": "grand_central",
        "name": "Grand Central Terminal",
        "address": "89 E 42nd St, New York, NY 10017",
        "description": "Historic train station with stunning celestial ceiling",
        "categories": ["architecture", "history", "landmarks"],
        "lat": 40.7527,
        "lng": -73.9772,
        "duration": 15,
        "image_url": "https://images.unsplash.com/photo-1520695287272-b7f8af46d367?w=1200&q=80"
    },
    {
        "id": "high_line",
        "name": "The High Line",
        "address": "High Line, New York, NY 10011",
        "description": "Elevated park built on historic freight rail line",
        "categories": ["parks", "art", "hidden gems"],
        "lat": 40.7480,
        "lng": -74.0048,
        "duration": 20,
        "image_url": "https://images.unsplash.com/photo-1568140384869-ed80ca8f8a48?w=1200&q=80"
    },
    {
        "id": "one_world_trade",
        "name": "One World Trade Center",
        "address": "285 Fulton St, New York, NY 10007",
        "description": "Tallest building in Western Hemisphere with 9/11 Memorial",
        "categories": ["landmarks", "history", "viewpoints"],
        "lat": 40.7127,
        "lng": -74.0134,
        "duration": 20,
        "image_url": "https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=1200&q=80"
    },
    {
        "id": "soho_district",
        "name": "SoHo",
        "address": "SoHo, New York, NY 10012",
        "description": "Trendy neighborhood with cast-iron architecture and boutiques",
        "categories": ["shopping", "neighborhoods", "art"],
        "lat": 40.7233,
        "lng": -74.0003,
        "duration": 25,
        "image_url": "https://images.unsplash.com/photo-1522083165195-3424ed129620?w=1200&q=80"
    }
]

def populate_firestore():
    """Populate Firestore with NYC locations."""
    db = firestore.Client(project=PROJECT_ID)
    locations_ref = db.collection('locations')

    print(f"🗽 Populating Firestore with {len(NYC_LOCATIONS)} NYC locations...")

    for location in NYC_LOCATIONS:
        doc_ref = locations_ref.document(location['id'])
        doc_ref.set(location)
        print(f"  ✅ Added: {location['name']}")

    print(f"\n✅ Successfully populated {len(NYC_LOCATIONS)} NYC locations!")
    print(f"📍 Location range: {NYC_LOCATIONS[0]['lat']:.4f}, {NYC_LOCATIONS[0]['lng']:.4f}")

if __name__ == "__main__":
    populate_firestore()
