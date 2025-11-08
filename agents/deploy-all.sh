#!/bin/bash

# Deploy all AI agents to Cloud Run
# Usage: ./deploy-all.sh

set -e

PROJECT_ID="quickcast-477213"
REGION="europe-west1"

echo "🚀 Deploying Geo-Story AI Agents to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Deploy Tour Curator Agent
echo "📦 [1/4] Deploying Tour Curator Agent..."
gcloud run deploy tour-curator-agent \
  --source=./curator \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

echo "✅ Tour Curator Agent deployed!"
echo ""

# Deploy Route Optimizer Agent
echo "🗺️  [2/4] Deploying Route Optimizer Agent..."
gcloud run deploy route-optimizer-agent \
  --source=./optimizer \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

echo "✅ Route Optimizer Agent deployed!"
echo ""

# Deploy Storytelling Agent
echo "✍️  [3/4] Deploying Storytelling Agent..."
gcloud run deploy storytelling-agent \
  --source=./storyteller \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --memory=1Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=5

echo "✅ Storytelling Agent deployed!"
echo ""

# Deploy Content Moderator Agent
echo "🛡️  [4/4] Deploying Content Moderator Agent..."
gcloud run deploy content-moderator-agent \
  --source=./moderator \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

echo "✅ Content Moderator Agent deployed!"
echo ""

echo "🎉 All agents deployed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Set GEMINI_API_KEY secret: gcloud run services update storytelling-agent --update-secrets=GEMINI_API_KEY=gemini-api-key:latest"
echo "2. Setup Pub/Sub triggers: cd .. && ./setup-pubsub.sh"
echo "3. Test agents: ./test-agents.sh"
