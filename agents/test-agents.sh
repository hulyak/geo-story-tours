#!/bin/bash

# Test all AI agents
# Usage: ./test-agents.sh

set -e

PROJECT_ID="quickcast-477213"
REGION="europe-west1"

echo "🧪 Testing Geo-Story AI Agents..."
echo ""

# Get service URLs
CURATOR_URL=$(gcloud run services describe tour-curator-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
OPTIMIZER_URL=$(gcloud run services describe route-optimizer-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
STORYTELLER_URL=$(gcloud run services describe storytelling-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
MODERATOR_URL=$(gcloud run services describe content-moderator-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo "📍 Service URLs:"
echo "  Curator: $CURATOR_URL"
echo "  Optimizer: $OPTIMIZER_URL"
echo "  Storyteller: $STORYTELLER_URL"
echo "  Moderator: $MODERATOR_URL"
echo ""

# Test 1: Health checks
echo "🏥 [1/5] Testing health checks..."
curl -s "$CURATOR_URL/" | jq .
curl -s "$OPTIMIZER_URL/" | jq .
curl -s "$STORYTELLER_URL/" | jq .
curl -s "$MODERATOR_URL/" | jq .
echo "✅ All agents healthy!"
echo ""

# Test 2: Tour Curator
echo "🎯 [2/5] Testing Tour Curator Agent..."
TOUR_JSON=$(curl -s -X POST "$CURATOR_URL/curate" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "interests": ["history", "architecture"],
      "duration": 30,
      "accessibility": ["wheelchair_accessible"]
    },
    "start_location": {
      "lat": 40.7128,
      "lng": -74.0060
    }
  }')

echo "$TOUR_JSON" | jq .
TOUR_ID=$(echo "$TOUR_JSON" | jq -r '.tour.tour_id')
echo "✅ Tour curated: $TOUR_ID"
echo ""

# Test 3: Route Optimizer
echo "🗺️  [3/5] Testing Route Optimizer Agent..."
OPTIMIZED_JSON=$(curl -s -X POST "$OPTIMIZER_URL/optimize" \
  -H "Content-Type: application/json" \
  -d "$TOUR_JSON")
echo "$OPTIMIZED_JSON" | jq .
echo "✅ Route optimized!"
echo ""

# Test 4: Storytelling Agent (single story)
echo "✍️  [4/5] Testing Storytelling Agent..."
STORY_JSON=$(curl -s -X POST "$STORYTELLER_URL/generate-story" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "name": "Historic City Hall",
      "description": "Built in 1803, this neoclassical building served as the seat of government",
      "categories": ["history", "architecture"]
    },
    "context": {
      "audience": "family-friendly",
      "tour_theme": "architectural-heritage"
    }
  }')

echo "$STORY_JSON" | jq .
echo "✅ Story generated!"
echo ""

# Test 5: Content Moderator
echo "🛡️  [5/5] Testing Content Moderator Agent..."
curl -s "$MODERATOR_URL/" | jq .
echo "✅ Moderator ready!"
echo ""

echo "🎉 All tests passed!"
echo ""
echo "🚀 Next: Trigger full flow with Pub/Sub"
echo "Run: curl -X POST $CURATOR_URL/curate -H 'Content-Type: application/json' -d '{...}'"
echo "Watch Cloud Console Pub/Sub dashboard to see messages flow through agents!"
