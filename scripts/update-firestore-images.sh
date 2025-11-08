#!/bin/bash

# Update Firestore locations with new image URLs using PATCH
set -e

PROJECT_ID="durable-torus-477513-g3"
ACCESS_TOKEN=$(gcloud auth print-access-token)

echo "🚀 Updating Firestore location images..."
echo "Project: $PROJECT_ID"
echo ""

# Read JSON file
LOCATIONS_JSON=$(cat "$(dirname "$0")/locations-data-updated.json")

# Extract locations array and iterate
echo "$LOCATIONS_JSON" | jq -c '.locations[]' | while read -r location; do
    ID=$(echo "$location" | jq -r '.id')
    NAME=$(echo "$location" | jq -r '.name')
    IMAGE_URL=$(echo "$location" | jq -r '.image_url')

    # Update only the image_url field using PATCH
    RESPONSE=$(curl -s -X PATCH \
        "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/locations/$ID?updateMask.fieldPaths=image_url" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"fields\": {
            \"image_url\": {\"stringValue\": \"$IMAGE_URL\"}
        }}" 2>&1)

    if echo "$RESPONSE" | grep -q "error"; then
        echo "   ❌ $NAME - Error: $(echo "$RESPONSE" | jq -r '.error.message // .error' 2>/dev/null || echo "$RESPONSE")"
    else
        echo "   ✅ $NAME"
    fi
done

echo ""
echo "✨ Done! Location images have been updated in Firestore"
