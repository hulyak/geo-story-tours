# Adding More Locations to Geo-Story Tours

## Overview

Geo-Story Tours uses **Google Cloud Firestore** as its database. All location data is stored in the `locations` collection. This guide explains how to add more locations to expand your tour offerings to new cities and neighborhoods.

---

## Database Structure

### Collection: `locations`

Each location document has the following structure:

```json
{
  "id": "loc_unique_identifier",
  "name": "Location Name",
  "categories": ["category1", "category2"],
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "description": "Brief description (1-2 sentences)",
  "historical_context": "Detailed context for AI storytelling",
  "average_visit_minutes": 5,
  "accessibility": ["wheelchair_accessible", "elevator"],
  "best_time_to_visit": "morning",
  "admission": "free",
  "image_url": "https://images.unsplash.com/..."
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `loc_historic_city_hall`) |
| `name` | string | Yes | Display name of the location |
| `categories` | array | Yes | Categories like "history", "food", "art", "hidden gems" |
| `coordinates` | object | Yes | `latitude` and `longitude` as numbers |
| `description` | string | Yes | Short description (displayed on cards) |
| `historical_context` | string | No | Detailed context for AI story generation |
| `average_visit_minutes` | number | Yes | Typical visit duration (3-10 minutes) |
| `accessibility` | array | No | Accessibility features |
| `best_time_to_visit` | string | No | Recommended visiting time |
| `admission` | string | No | Entry requirements (free, paid, donation) |
| `image_url` | string | Yes | URL to location image (Unsplash recommended) |

---

## Method 1: Add via Firestore Console (Easiest)

### Step 1: Open Firestore Console
```bash
# Open in browser
https://console.cloud.google.com/firestore/databases/-default-/data/panel/locations?project=durable-torus-477513-g3
```

### Step 2: Create New Document
1. Click **"Add Document"**
2. Set Document ID: `loc_your_location_name`
3. Add each field as shown in the structure above
4. Click **"Save"**

### Step 3: Verify
```bash
# Visit your frontend to see the new location
https://geo-story-frontend-168041541697.europe-west1.run.app
```

---

## Method 2: Add via Upload Script (Bulk)

### Step 1: Edit locations.json

Edit `/seed-data/locations.json` and add your new locations:

```json
{
  "id": "loc_eiffel_tower",
  "name": "Eiffel Tower",
  "categories": ["history", "architecture", "iconic"],
  "coordinates": {
    "latitude": 48.8584,
    "longitude": 2.2945
  },
  "description": "Iconic iron lattice tower on the Champ de Mars, built in 1889.",
  "historical_context": "Constructed for the 1889 World's Fair, it was initially criticized but became France's most recognizable symbol.",
  "average_visit_minutes": 45,
  "accessibility": ["elevator", "stairs", "restroom"],
  "best_time_to_visit": "sunrise",
  "admission": "paid",
  "image_url": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f"
}
```

### Step 2: Upload via Script

```bash
cd /seed-data

# Run the upload script
./upload-via-rest.sh
```

### Step 3: Verify Upload

```bash
# Check API response
curl -s https://geo-story-frontend-168041541697.europe-west1.run.app/api/locations | jq '.locations | length'

# Should show increased number
```

---

## Method 3: Add via Firestore SDK (Programmatic)

Create a script to add locations programmatically:

```python
from google.cloud import firestore

# Initialize Firestore
db = firestore.Client(project='durable-torus-477513-g3')

# New location data
new_location = {
    "id": "loc_colosseum",
    "name": "The Colosseum",
    "categories": ["history", "architecture", "ancient"],
    "coordinates": {
        "latitude": 41.8902,
        "longitude": 12.4922
    },
    "description": "Ancient amphitheater in the center of Rome, built in 70-80 AD.",
    "historical_context": "The largest amphitheater ever built, it could hold 50,000 spectators and hosted gladiatorial contests.",
    "average_visit_minutes": 60,
    "accessibility": ["wheelchair_accessible", "restroom", "audio_guide"],
    "best_time_to_visit": "morning",
    "admission": "paid",
    "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5"
}

# Add to Firestore
db.collection('locations').document(new_location['id']).set(new_location)
print(f"Added location: {new_location['name']}")
```

---

## Finding Geographic Coordinates

### Option 1: Google Maps
1. Go to https://www.google.com/maps
2. Right-click on the location
3. Click coordinates to copy
4. Format: `latitude, longitude`

### Option 2: Geocoding API

```bash
# Get coordinates for an address
ADDRESS="Eiffel Tower, Paris"
curl "https://maps.googleapis.com/maps/api/geocode/json?address=${ADDRESS}&key=YOUR_API_KEY" | jq '.results[0].geometry.location'
```

---

## Finding Images

### Recommended: Unsplash

1. Visit https://unsplash.com
2. Search for your location
3. Copy the photo URL (choose size: `?w=800`)
4. Example: `https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=800`

### Requirements:
- High quality (min 1200x800px)
- Free to use (Unsplash, Pexels, Pixabay)
- Represents the location accurately

---

## Available Categories

Current categories supported in the frontend:

- `all` (default, shows everything)
- `history`
- `food`
- `art`
- `hidden gems`

### To Add New Categories:

Edit `/app/page.tsx` line 12:

```typescript
const categories = ['all', 'history', 'food', 'art', 'hidden gems', 'nature', 'architecture'];
```

---

## Expanding to New Cities

### Example: Adding Paris Locations

1. **Create 10+ locations** in the same neighborhood
2. **Use similar coordinates** (within 0.01 degrees)
3. **Add city identifier** to the `id` field:
   ```
   loc_paris_eiffel_tower
   loc_paris_louvre
   loc_paris_notre_dame
   ```

4. **Update tour curator agent** to filter by city:
   ```python
   # In agents/curator/agent.py
   locations = db.collection('locations').where('city', '==', 'paris').get()
   ```

### Recommended City Structure

For best results, add:
- **10-15 locations** per city
- **Mix of categories** (history, food, art)
- **Walking distance** (0.5-1 mile radius)
- **Varied visit durations** (3-10 minutes each)

---

## Database Scalability

### Current Setup
- **Database**: Cloud Firestore (serverless)
- **Auto-scaling**: Yes
- **Cost**: Pay-per-use (free tier: 50K reads/day)
- **Limits**: 1M documents (more than enough)

### Multi-City Support

To support multiple cities efficiently:

```javascript
// Add city field to each location
{
  "id": "loc_paris_eiffel_tower",
  "city": "paris",
  "country": "france",
  // ... rest of fields
}

// Query locations by city
const locations = await db.collection('locations')
  .where('city', '==', 'paris')
  .get();
```

---

## Testing New Locations

### 1. Check API Response

```bash
curl -s https://geo-story-frontend-168041541697.europe-west1.run.app/api/locations | jq '.locations[] | select(.id == "loc_your_new_location")'
```

### 2. Test in Frontend

1. Visit https://geo-story-frontend-168041541697.europe-west1.run.app
2. Look for your new location in the grid
3. Click to verify modal displays correctly
4. Check coordinates link to Google Maps

### 3. Test in Tours

1. Click "Create Your Tour"
2. Verify new location is included in AI-generated tours
3. Check that stories are generated correctly

---

## Best Practices

### ✅ DO:
- Use descriptive IDs with `loc_` prefix
- Provide rich `historical_context` for better AI stories
- Use high-quality images (800px+ width)
- Include accurate coordinates (4+ decimal places)
- Add multiple categories for discoverability

### ❌ DON'T:
- Use duplicate IDs
- Leave `coordinates` empty (required for maps)
- Use copyrighted images
- Mix locations from different continents in one tour
- Add locations without descriptions

---

## Monitoring Database Usage

```bash
# View Firestore metrics
gcloud firestore operations list --database=(default)

# Check read/write operations
gcloud logging read "resource.type=cloud_firestore_database" --limit=50

# Monitor costs
gcloud billing accounts list
```

---

## Example: Complete New Location

```json
{
  "id": "loc_london_tower_bridge",
  "name": "Tower Bridge",
  "city": "london",
  "country": "uk",
  "categories": ["history", "architecture", "iconic", "photography"],
  "coordinates": {
    "latitude": 51.5055,
    "longitude": -0.0754
  },
  "description": "Victorian bascule bridge spanning the River Thames, completed in 1894.",
  "historical_context": "Designed by Sir Horace Jones and engineered by Sir John Wolfe Barry, it took 8 years and 432 workers to build. The bridge's distinctive twin towers house the original hydraulic engines that powered the bascules. It opens approximately 800 times per year to allow tall ships to pass.",
  "average_visit_minutes": 8,
  "accessibility": ["wheelchair_accessible", "elevator", "restroom", "gift_shop"],
  "best_time_to_visit": "sunset",
  "admission": "paid",
  "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800"
}
```

---

## Support

If you encounter issues adding locations:

1. **Check Firestore permissions**: Ensure Cloud Run service account has write access
2. **Verify JSON format**: Use a JSON validator
3. **Test coordinates**: Paste into Google Maps to verify
4. **Check logs**: `gcloud logging read "resource.labels.service_name=geo-story-frontend" --limit=20`

---

## Future Enhancements

Planned features for location management:

- [ ] Admin dashboard for adding locations via UI
- [ ] Bulk import from CSV
- [ ] Image upload to Cloud Storage
- [ ] Automated geocoding from addresses
- [ ] Location verification workflow
- [ ] User-submitted locations (moderated)


