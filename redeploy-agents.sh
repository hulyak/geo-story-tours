#!/bin/bash

# Redeploy Storytelling and Voice Synthesis Agents with fixed code

set -e

PROJECT_ID="durable-torus-477513-g3"
REGION="europe-west1"

echo "🚀 Redeploying Storytelling and Voice Synthesis Agents..."
echo ""

# Deploy Storytelling Agent
echo "📖 Deploying Storytelling Agent..."
cd agents/storyteller
gcloud run deploy storytelling-agent \
  --source=. \
  --region=$REGION \
  --memory=1Gi \
  --cpu=2 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

echo ""
echo "✅ Storytelling Agent deployed!"
echo ""

# Deploy Voice Synthesis Agent
echo "🎤 Deploying Voice Synthesis Agent..."
cd ../voice-synthesis
gcloud run deploy voice-synthesis-agent \
  --source=. \
  --region=$REGION \
  --memory=16Gi \
  --cpu=4 \
  --timeout=600 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

echo ""
echo "✅ Voice Synthesis Agent deployed!"
echo ""

# Test the agents
echo "🧪 Testing agents..."
echo ""

echo "Testing Storytelling Agent..."
curl -s https://storytelling-agent-168041541697.europe-west1.run.app/ | jq .

echo ""
echo "Testing Voice Synthesis Agent..."
curl -s https://voice-synthesis-agent-168041541697.europe-west1.run.app/ | jq .

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo ""
echo "Create a new tour to test AI story generation!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
