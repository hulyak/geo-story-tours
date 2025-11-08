#!/bin/bash

PROJECT_ID="durable-torus-477513-g3"
TOKEN=$(gcloud auth print-access-token)

# Read each location from JSON and upload via REST API
cat locations.json | jq -c '.[]' | while read location; do
  LOC_ID=$(echo $location | jq -r '.id')
  echo "Uploading: $LOC_ID"

  curl -X PATCH \
    "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/locations/$LOC_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"fields\": $(echo $location | jq '{
      id: {stringValue: .id},
      name: {stringValue: .name},
      categories: {arrayValue: {values: [.categories[] | {stringValue: .}]}},
      coordinates: {mapValue: {fields: {
        lat: {doubleValue: .coordinates.lat},
        lng: {doubleValue: .coordinates.lng}
      }}},
      description: {stringValue: .description},
      historical_context: {stringValue: .historical_context},
      average_visit_minutes: {integerValue: .average_visit_minutes | tostring},
      accessibility: {arrayValue: {values: [.accessibility[] | {stringValue: .}]}},
      best_time_to_visit: {stringValue: .best_time_to_visit},
      admission: {stringValue: .admission},
      image_url: {stringValue: .image_url}
    }')}"
done

echo "✅ Upload complete!"
