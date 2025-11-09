#!/bin/bash

# Cleanup old/duplicate Cloud Run services
# These are the old services that were replaced with new naming convention

set -e

PROJECT_ID="durable-torus-477513-g3"
REGION="europe-west1"

echo "🧹 Cleaning up old/duplicate Cloud Run services..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Delete old services (replaced by new ones with hyphenated names)
OLD_SERVICES=(
  "curator-agent"
  "moderator-agent"
  "optimizer-agent"
  "storyteller-agent"
)

for service in "${OLD_SERVICES[@]}"; do
  echo "🗑️  Deleting $service..."
  gcloud run services delete "$service" \
    --region=$REGION \
    --quiet || echo "⚠️  Service $service not found or already deleted"
  echo ""
done

echo "✅ Cleanup completed!"
echo ""
echo "Remaining services:"
gcloud run services list --region=$REGION --format="table(SERVICE,REGION,URL)"
