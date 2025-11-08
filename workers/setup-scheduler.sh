#!/bin/bash

# Setup Cloud Scheduler Jobs
# Based on JOBS_AND_WORKERS.md specifications

set -e

PROJECT_ID="durable-torus-477513-g3"
PROJECT_NUMBER="168041541697"
REGION="europe-west1"
SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

echo "⏰ Setting up Cloud Scheduler Jobs..."
echo "Project: $PROJECT_ID"
echo ""

# Analytics aggregation - Daily at midnight
echo "📊 Creating Analytics Aggregation Schedule (daily at midnight)..."
gcloud scheduler jobs create http analytics-cron \
  --location=$REGION \
  --schedule="0 0 * * *" \
  --uri="https://$REGION-run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/jobs/analytics-worker:run" \
  --http-method=POST \
  --oauth-service-account-email=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --time-zone="UTC" \
  --description="Daily analytics aggregation at midnight UTC" \
  2>&1 || echo "Job already exists, updating..."

gcloud scheduler jobs update http analytics-cron \
  --location=$REGION \
  --schedule="0 0 * * *" \
  --uri="https://$REGION-run.googleapis.com/v2/projects/$PROJECT_ID/locations/$REGION/jobs/analytics-worker:run" \
  --project=$PROJECT_ID \
  2>&1 || true

echo "✅ Analytics schedule created"
echo ""

# Voice synthesis batch - Every 5 minutes
echo "🎙️ Creating Voice Synthesis Schedule (every 5 minutes)..."
gcloud scheduler jobs create http voice-synthesis-cron \
  --location=us-central1 \
  --schedule="*/5 * * * *" \
  --uri="https://us-central1-run.googleapis.com/v2/projects/$PROJECT_ID/locations/us-central1/jobs/voice-synthesis-worker:run" \
  --http-method=POST \
  --oauth-service-account-email=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --time-zone="UTC" \
  --description="Voice synthesis batch processing every 5 minutes" \
  2>&1 || echo "Job already exists, updating..."

gcloud scheduler jobs update http voice-synthesis-cron \
  --location=us-central1 \
  --schedule="*/5 * * * *" \
  --uri="https://us-central1-run.googleapis.com/v2/projects/$PROJECT_ID/locations/us-central1/jobs/voice-synthesis-worker:run" \
  --project=$PROJECT_ID \
  2>&1 || true

echo "✅ Voice synthesis schedule created"
echo ""

echo "🎉 All Cloud Scheduler jobs configured!"
echo ""
echo "To view jobs:"
echo "  gcloud scheduler jobs list --location=$REGION"
echo ""
echo "To manually trigger:"
echo "  gcloud scheduler jobs run analytics-cron --location=$REGION"
echo "  gcloud scheduler jobs run voice-synthesis-cron --location=us-central1"
