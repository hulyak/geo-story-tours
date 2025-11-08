#!/bin/bash

# Setup Pub/Sub topics and subscriptions for agent communication
# Usage: ./setup-pubsub.sh

set -e

PROJECT_ID="quickcast-477213"
REGION="europe-west1"

echo "🔗 Setting up Pub/Sub for agent communication..."
echo "Project: $PROJECT_ID"
echo ""

# Create topics
echo "📢 Creating Pub/Sub topics..."

gcloud pubsub topics create route-planned --project=$PROJECT_ID || echo "Topic route-planned already exists"
gcloud pubsub topics create route-optimized --project=$PROJECT_ID || echo "Topic route-optimized already exists"
gcloud pubsub topics create stories-generated --project=$PROJECT_ID || echo "Topic stories-generated already exists"

echo "✅ Topics created!"
echo ""

# Create push subscriptions to Cloud Run services
echo "📮 Creating push subscriptions..."

# Route Optimizer subscribes to route-planned
OPTIMIZER_URL=$(gcloud run services describe route-optimizer-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
gcloud pubsub subscriptions create route-planned-sub \
  --topic=route-planned \
  --push-endpoint="${OPTIMIZER_URL}/pubsub" \
  --project=$PROJECT_ID || echo "Subscription route-planned-sub already exists"

# Storytelling Agent subscribes to route-optimized
STORYTELLER_URL=$(gcloud run services describe storytelling-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
gcloud pubsub subscriptions create route-optimized-sub \
  --topic=route-optimized \
  --push-endpoint="${STORYTELLER_URL}/pubsub" \
  --project=$PROJECT_ID || echo "Subscription route-optimized-sub already exists"

# Content Moderator subscribes to stories-generated
MODERATOR_URL=$(gcloud run services describe content-moderator-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
gcloud pubsub subscriptions create stories-generated-sub \
  --topic=stories-generated \
  --push-endpoint="${MODERATOR_URL}/pubsub" \
  --project=$PROJECT_ID || echo "Subscription stories-generated-sub already exists"

echo "✅ Subscriptions created!"
echo ""

echo "🎉 Pub/Sub setup complete!"
echo ""
echo "📊 Agent Communication Flow:"
echo "1. Tour Curator → Pub/Sub: route-planned → Route Optimizer"
echo "2. Route Optimizer → Pub/Sub: route-optimized → Storytelling Agent"
echo "3. Storytelling Agent → Pub/Sub: stories-generated → Content Moderator"
echo ""
echo "🔍 Test the flow:"
echo "curl -X POST https://tour-curator-agent-URL/curate -H 'Content-Type: application/json' -d '{\"preferences\": {\"interests\": [\"history\"]}}'"
