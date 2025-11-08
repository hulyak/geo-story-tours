#!/usr/bin/env python3
"""
Upload mock location data to Firestore

Usage:
  python upload-to-firestore.py
"""

import json
from google.cloud import firestore

PROJECT_ID = "durable-torus-477513-g3"

def upload_locations():
    """Upload location data to Firestore"""

    # Initialize Firestore
    db = firestore.Client(project=PROJECT_ID)
    locations_ref = db.collection('locations')

    # Load JSON data
    with open('locations.json', 'r') as f:
        locations = json.load(f)

    print(f"📍 Uploading {len(locations)} locations to Firestore...")

    # Upload each location
    for location in locations:
        loc_id = location['id']
        locations_ref.document(loc_id).set(location)
        print(f"  ✅ Uploaded: {location['name']}")

    print(f"\n🎉 Successfully uploaded {len(locations)} locations!")
    print(f"\n📊 Categories:")
    categories = set()
    for loc in locations:
        categories.update(loc['categories'])
    for cat in sorted(categories):
        count = sum(1 for loc in locations if cat in loc['categories'])
        print(f"  - {cat}: {count} locations")

if __name__ == "__main__":
    upload_locations()
