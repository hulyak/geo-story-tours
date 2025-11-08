#!/bin/bash

# Deploy Workers to Cloud Run Jobs
# Based on JOBS_AND_WORKERS.md specifications

set -e

PROJECT_ID="durable-torus-477513-g3"
REGION="europe-west1"

echo "🚀 Deploying Workers to Cloud Run Jobs..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Build and deploy analytics worker
echo "📊 Building Analytics Aggregation Worker..."
cd "$(dirname "$0")"

# Build using Cloud Build with explicit config
cat > cloudbuild-analytics.yaml <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/analytics-worker', '-f', 'Dockerfile.analytics', '.']
images:
- 'gcr.io/$PROJECT_ID/analytics-worker'
EOF

gcloud builds submit --config=cloudbuild-analytics.yaml --project=$PROJECT_ID

echo "📊 Creating Analytics Worker Job..."
gcloud run jobs create analytics-worker \
  --image=gcr.io/$PROJECT_ID/analytics-worker \
  --region=$REGION \
  --memory=1Gi \
  --cpu=1 \
  --max-retries=3 \
  --task-timeout=10m \
  --project=$PROJECT_ID \
  || echo "Job already exists, updating..."

gcloud run jobs update analytics-worker \
  --image=gcr.io/$PROJECT_ID/analytics-worker \
  --region=$REGION \
  --project=$PROJECT_ID \
  || true

echo "✅ Analytics worker deployed"
echo ""

# Build and deploy voice synthesis worker (with GPU)
echo "🎙️ Building Voice Synthesis Worker..."
cat > cloudbuild-voice.yaml <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/voice-synthesis-worker', '-f', 'Dockerfile.voice-synthesis', '.']
images:
- 'gcr.io/$PROJECT_ID/voice-synthesis-worker'
EOF

gcloud builds submit --config=cloudbuild-voice.yaml --project=$PROJECT_ID

echo "🎙️ Creating Voice Synthesis Worker Job..."
gcloud run jobs create voice-synthesis-worker \
  --image=gcr.io/$PROJECT_ID/voice-synthesis-worker \
  --region=us-central1 \
  --memory=16Gi \
  --cpu=4 \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --max-retries=2 \
  --task-timeout=30m \
  --project=$PROJECT_ID \
  || echo "Job already exists, updating..."

gcloud run jobs update voice-synthesis-worker \
  --image=gcr.io/$PROJECT_ID/voice-synthesis-worker \
  --region=us-central1 \
  --project=$PROJECT_ID \
  || true

echo "✅ Voice synthesis worker deployed"
echo ""

echo "🎉 All workers deployed successfully!"
echo ""
echo "To run jobs manually:"
echo "  gcloud run jobs execute analytics-worker --region=$REGION"
echo "  gcloud run jobs execute voice-synthesis-worker --region=us-central1"
