#!/bin/bash

# Populate Firestore using REST API with gcloud auth token
set -e

PROJECT_ID="durable-torus-477513-g3"
ACCESS_TOKEN=$(gcloud auth print-access-token)

echo "🚀 Populating Firestore with locations..."
echo "Project: $PROJECT_ID"
echo ""

# Read JSON file
LOCATIONS_JSON=$(cat "$(dirname "$0")/locations-data-updated.json")

# Extract locations array and iterate
echo "$LOCATIONS_JSON" | jq -c '.locations[]' | while read -r location; do
    ID=$(echo "$location" | jq -r '.id')
    NAME=$(echo "$location" | jq -r '.name')
    CATEGORIES=$(echo "$location" | jq -c '.categories')

    # Remove 'id' field from the document data
    DOC_DATA=$(echo "$location" | jq 'del(.id)')

    # Create document in Firestore
    RESPONSE=$(curl -s -X POST \
        "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/locations?documentId=$ID" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"fields\": $(echo "$DOC_DATA" | jq -c '{
            name: {stringValue: .name},
            lat: {doubleValue: .lat},
            lng: {doubleValue: .lng},
            categories: {arrayValue: {values: [.categories[] | {stringValue: .}]}},
            description: {stringValue: .description},
            address: {stringValue: .address},
            image_url: {stringValue: .image_url},
            duration: {integerValue: (.duration | tostring)}
        }')}" 2>&1)

    if echo "$RESPONSE" | grep -q "error"; then
        echo "   ❌ $NAME - Error"
    else
        echo "   ✅ $NAME ($(echo "$CATEGORIES" | jq -r 'join(", ")'))"
    fi
done

echo ""
echo "✨ Done! Locations have been added to Firestore"
echo ""
echo "🎯 Your tour agents can now select from these locations!"
