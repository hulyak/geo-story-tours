#!/usr/bin/env python3
"""
Populate Firestore with sample locations for Geo Story Tours
"""

from google.cloud import firestore
import json
import os

PROJECT_ID = "durable-torus-477513-g3"

def load_locations():
    """Load locations from JSON file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'locations-data-updated.json')

    with open(json_file, 'r') as f:
        data = json.load(f)

    return data['locations']

def populate_firestore():
    """Populate Firestore with sample locations"""
    print(f"🚀 Connecting to Firestore (Project: {PROJECT_ID})")
    db = firestore.Client(project=PROJECT_ID)

    locations_ref = db.collection('locations')

    # Load locations from JSON file
    print(f"\n📂 Loading locations from JSON file...")
    locations = load_locations()

    print(f"\n📝 Adding {len(locations)} locations to Firestore...")

    for i, location in enumerate(locations, 1):
        # Generate doc ID from name (or use 'id' field if present)
        doc_id = location.get('id') or location['name'].lower().replace(' ', '_').replace("'", '')

        # Remove 'id' field before storing if it exists
        location_data = {k: v for k, v in location.items() if k != 'id'}

        try:
            locations_ref.document(doc_id).set(location_data)
            print(f"   {i}. ✅ {location['name']} ({', '.join(location['categories'])})")
        except Exception as e:
            print(f"   {i}. ❌ {location['name']} - Error: {e}")

    print(f"\n✨ Done! Added {len(locations)} locations to Firestore")
    print(f"\n🎯 Your tour agents can now select from these locations!")
    print(f"\n📍 Categories available:")
    categories = set()
    for loc in locations:
        categories.update(loc['categories'])
    for cat in sorted(categories):
        count = sum(1 for loc in locations if cat in loc['categories'])
        print(f"   - {cat}: {count} locations")

if __name__ == "__main__":
    populate_firestore()
