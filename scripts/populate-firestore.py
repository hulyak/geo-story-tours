#!/usr/bin/env python3
"""
Populate Firestore with sample locations for Geo Story Tours
"""

from google.cloud import firestore
import os

PROJECT_ID = "durable-torus-477513-g3"

# Sample locations for Paris
SAMPLE_LOCATIONS = [
    {
        "name": "Eiffel Tower",
        "lat": 48.8584,
        "lng": 2.2945,
        "categories": ["history", "landmarks"],
        "description": "The iconic iron lattice tower, symbol of Paris",
        "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
        "image_url": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=800",
        "duration": 15
    },
    {
        "name": "Louvre Museum",
        "lat": 48.8606,
        "lng": 2.3376,
        "categories": ["art", "history", "museums"],
        "description": "World's largest art museum and historic monument",
        "address": "Rue de Rivoli, 75001 Paris",
        "image_url": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800",
        "duration": 20
    },
    {
        "name": "Notre-Dame Cathedral",
        "lat": 48.8530,
        "lng": 2.3499,
        "categories": ["history", "architecture"],
        "description": "Medieval Catholic cathedral with Gothic architecture",
        "address": "6 Parvis Notre-Dame, 75004 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Montmartre",
        "lat": 48.8867,
        "lng": 2.3431,
        "categories": ["hidden gems", "art", "neighborhoods"],
        "description": "Historic hilltop neighborhood with artistic heritage",
        "address": "Montmartre, 75018 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Le Marais",
        "lat": 48.8584,
        "lng": 2.3622,
        "categories": ["neighborhoods", "food", "shopping"],
        "description": "Trendy district with medieval streets and boutiques",
        "address": "Le Marais, 75003-75004 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Sainte-Chapelle",
        "lat": 48.8554,
        "lng": 2.3450,
        "categories": ["history", "architecture", "hidden gems"],
        "description": "Royal chapel with stunning stained glass windows",
        "address": "8 Boulevard du Palais, 75001 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 10
    },
    {
        "name": "Luxembourg Gardens",
        "lat": 48.8462,
        "lng": 2.3372,
        "categories": ["parks", "relaxation"],
        "description": "Beautiful gardens with palace and fountains",
        "address": "Rue de Médicis, 75006 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Musée d'Orsay",
        "lat": 48.8600,
        "lng": 2.3266,
        "categories": ["art", "museums", "history"],
        "description": "Impressionist and post-Impressionist art museum",
        "address": "1 Rue de la Légion d'Honneur, 75007 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Sacré-Cœur Basilica",
        "lat": 48.8867,
        "lng": 2.3431,
        "categories": ["history", "architecture", "landmarks"],
        "description": "White-domed basilica atop Montmartre hill",
        "address": "35 Rue du Chevalier de la Barre, 75018 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Champs-Élysées",
        "lat": 48.8698,
        "lng": 2.3078,
        "categories": ["shopping", "landmarks"],
        "description": "Famous avenue with shops, cafés, and theaters",
        "address": "Avenue des Champs-Élysées, 75008 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Latin Quarter",
        "lat": 48.8506,
        "lng": 2.3444,
        "categories": ["neighborhoods", "history", "hidden gems"],
        "description": "Historic area around the Sorbonne university",
        "address": "Latin Quarter, 75005 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Arc de Triomphe",
        "lat": 48.8738,
        "lng": 2.2950,
        "categories": ["history", "landmarks"],
        "description": "Iconic triumphal arch honoring war heroes",
        "address": "Place Charles de Gaulle, 75008 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 10
    },
    {
        "name": "Shakespeare and Company",
        "lat": 48.8525,
        "lng": 2.3470,
        "categories": ["hidden gems", "culture", "shopping"],
        "description": "Historic English-language bookstore",
        "address": "37 Rue de la Bûcherie, 75005 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 10
    },
    {
        "name": "Père Lachaise Cemetery",
        "lat": 48.8619,
        "lng": 2.3932,
        "categories": ["hidden gems", "history"],
        "description": "Famous cemetery with notable graves",
        "address": "16 Rue du Repos, 75020 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Centre Pompidou",
        "lat": 48.8606,
        "lng": 2.3522,
        "categories": ["art", "museums", "architecture"],
        "description": "Modern art museum with radical architecture",
        "address": "Place Georges-Pompidou, 75004 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Tuileries Garden",
        "lat": 48.8635,
        "lng": 2.3275,
        "categories": ["parks", "relaxation"],
        "description": "Public garden between Louvre and Place de la Concorde",
        "address": "Place de la Concorde, 75001 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Rodin Museum",
        "lat": 48.8553,
        "lng": 2.3159,
        "categories": ["art", "museums", "hidden gems"],
        "description": "Museum dedicated to sculptor Auguste Rodin",
        "address": "77 Rue de Varenne, 75007 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Panthéon",
        "lat": 48.8462,
        "lng": 2.3461,
        "categories": ["history", "architecture", "landmarks"],
        "description": "Neoclassical mausoleum for notable French citizens",
        "address": "Place du Panthéon, 75005 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 10
    },
    {
        "name": "Palais Garnier",
        "lat": 48.8720,
        "lng": 2.3318,
        "categories": ["art", "architecture", "culture"],
        "description": "Opulent opera house with ornate interiors",
        "address": "Place de l'Opéra, 75009 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Rue Crémieux",
        "lat": 48.8461,
        "lng": 2.3795,
        "categories": ["hidden gems", "photography"],
        "description": "Colorful pedestrian street perfect for photos",
        "address": "Rue Crémieux, 75012 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 5
    },
    {
        "name": "Marché des Enfants Rouges",
        "lat": 48.8634,
        "lng": 2.3644,
        "categories": ["food", "hidden gems", "markets"],
        "description": "Oldest covered market in Paris",
        "address": "39 Rue de Bretagne, 75003 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Canal Saint-Martin",
        "lat": 48.8733,
        "lng": 2.3650,
        "categories": ["neighborhoods", "hidden gems", "relaxation"],
        "description": "Trendy waterway with locks and footbridges",
        "address": "Canal Saint-Martin, 75010 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Promenade Plantée",
        "lat": 48.8485,
        "lng": 2.3765,
        "categories": ["parks", "hidden gems"],
        "description": "Elevated park built on old railway viaduct",
        "address": "Coulée verte René-Dumont, 75012 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 20
    },
    {
        "name": "Galeries Lafayette",
        "lat": 48.8737,
        "lng": 2.3320,
        "categories": ["shopping", "architecture"],
        "description": "Luxury department store with stunning glass dome",
        "address": "40 Boulevard Haussmann, 75009 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
    {
        "name": "Musée Picasso",
        "lat": 48.8597,
        "lng": 2.3625,
        "categories": ["art", "museums"],
        "description": "Museum dedicated to works of Pablo Picasso",
        "address": "5 Rue de Thorigny, 75003 Paris",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "duration": 15
    },
]

def populate_firestore():
    """Populate Firestore with sample locations"""
    print(f"🚀 Connecting to Firestore (Project: {PROJECT_ID})")
    db = firestore.Client(project=PROJECT_ID)

    locations_ref = db.collection('locations')

    print(f"\n📝 Adding {len(SAMPLE_LOCATIONS)} locations to Firestore...")

    for i, location in enumerate(SAMPLE_LOCATIONS, 1):
        # Generate doc ID from name
        doc_id = location['name'].lower().replace(' ', '_').replace("'", '')

        try:
            locations_ref.document(doc_id).set(location)
            print(f"   {i}. ✅ {location['name']} ({', '.join(location['categories'])})")
        except Exception as e:
            print(f"   {i}. ❌ {location['name']} - Error: {e}")

    print(f"\n✨ Done! Added {len(SAMPLE_LOCATIONS)} locations to Firestore")
    print(f"\n🎯 Your tour agents can now select from these locations!")
    print(f"\n📍 Categories available:")
    categories = set()
    for loc in SAMPLE_LOCATIONS:
        categories.update(loc['categories'])
    for cat in sorted(categories):
        count = sum(1 for loc in SAMPLE_LOCATIONS if cat in loc['categories'])
        print(f"   - {cat}: {count} locations")

if __name__ == "__main__":
    populate_firestore()
