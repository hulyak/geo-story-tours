#!/bin/bash

# Diagnostic Script for Geo-Story Tours
# Checks the current state of all services and identifies issues

PROJECT_ID="durable-torus-477513-g3"
REGION="europe-west1"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Geo-Story Tours Diagnostic Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check Google Maps APIs
echo -e "${BLUE}📍 Google Maps APIs Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MAPS_APIS=(
    "maps-backend.googleapis.com:Maps JavaScript API"
    "places-backend.googleapis.com:Places API"
    "geocoding-backend.googleapis.com:Geocoding API"
    "directions-backend.googleapis.com:Directions API"
)

for API_INFO in "${MAPS_APIS[@]}"; do
    API=$(echo $API_INFO | cut -d: -f1)
    NAME=$(echo $API_INFO | cut -d: -f2)
    
    if gcloud services list --enabled --project=$PROJECT_ID 2>/dev/null | grep -q "$API"; then
        echo -e "${GREEN}✓${NC} $NAME: Enabled"
    else
        echo -e "${RED}✗${NC} $NAME: Disabled"
    fi
done
echo ""

# 2. Check Google Maps API Key
echo -e "${BLUE}🗺️ Google Maps API Key${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env.local" ]; then
    API_KEY=$(grep NEXT_PUBLIC_GOOGLE_MAPS_API_KEY .env.local | cut -d= -f2)
    if [ -n "$API_KEY" ]; then
        echo -e "${GREEN}✓${NC} API Key found in .env.local"
        echo "  Key: ${API_KEY:0:20}..."
        
        # Test the key
        RESPONSE=$(curl -s "https://maps.googleapis.com/maps/api/js?key=$API_KEY")
        if echo "$RESPONSE" | grep -q "Google Maps JavaScript API"; then
            echo -e "${GREEN}✓${NC} API Key is valid"
        else
            echo -e "${RED}✗${NC} API Key may be invalid or restricted"
        fi
    else
        echo -e "${RED}✗${NC} API Key not found in .env.local"
    fi
else
    echo -e "${RED}✗${NC} .env.local file not found"
fi
echo ""

# 3. Check Agent Health
echo -e "${BLUE}🤖 Agent Health Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AGENTS=(
    "tour-curator-agent:https://tour-curator-agent-168041541697.europe-west1.run.app"
    "route-optimizer-agent:https://route-optimizer-agent-168041541697.europe-west1.run.app"
    "storytelling-agent:https://storytelling-agent-168041541697.europe-west1.run.app"
    "content-moderator-agent:https://content-moderator-agent-168041541697.europe-west1.run.app"
    "voice-synthesis-agent:https://voice-synthesis-agent-168041541697.europe-west1.run.app"
    "tour-orchestrator:https://tour-orchestrator-168041541697.europe-west1.run.app"
)

for AGENT_INFO in "${AGENTS[@]}"; do
    NAME=$(echo $AGENT_INFO | cut -d: -f1)
    URL=$(echo $AGENT_INFO | cut -d: -f2-)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "$URL/" 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} $NAME: Healthy"
        if echo "$BODY" | grep -q "model"; then
            MODEL=$(echo "$BODY" | grep -o '"model":"[^"]*"' | cut -d'"' -f4)
            TOOLS=$(echo "$BODY" | grep -o '"tools":[0-9]*' | cut -d: -f2)
            echo "    Model: $MODEL, Tools: $TOOLS"
        fi
    else
        echo -e "${RED}✗${NC} $NAME: Not responding (HTTP $HTTP_CODE)"
    fi
done
echo ""

# 4. Check Gemini API Key Secret
echo -e "${BLUE}🔑 Gemini API Key Secret${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud secrets describe gemini-api-key --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}✓${NC} Secret 'gemini-api-key' exists"
    
    # Check if service account has access
    PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    
    if gcloud secrets get-iam-policy gemini-api-key --project=$PROJECT_ID 2>/dev/null | grep -q "$SERVICE_ACCOUNT"; then
        echo -e "${GREEN}✓${NC} Service account has access to secret"
    else
        echo -e "${RED}✗${NC} Service account cannot access secret"
    fi
else
    echo -e "${RED}✗${NC} Secret 'gemini-api-key' not found"
fi
echo ""

# 5. Check Firestore Permissions
echo -e "${BLUE}🔐 Firestore Permissions${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

if gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:$SERVICE_ACCOUNT" 2>/dev/null | grep -q "datastore.user"; then
    echo -e "${GREEN}✓${NC} Service account has Firestore access"
else
    echo -e "${RED}✗${NC} Service account lacks Firestore permissions"
fi
echo ""

# 6. Check Firestore Data
echo -e "${BLUE}📊 Firestore Data${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Try to count documents (this is a rough check)
echo "Checking collections..."
gcloud firestore databases describe --database="(default)" --project=$PROJECT_ID &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Firestore database exists"
    echo "  Note: Use Firebase Console to view data"
    echo "  https://console.firebase.google.com/project/$PROJECT_ID/firestore"
else
    echo -e "${RED}✗${NC} Cannot access Firestore database"
fi
echo ""

# 7. Check Frontend Deployment
echo -e "${BLUE}🌐 Frontend Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FRONTEND_URL="https://geo-story-frontend-168041541697.europe-west1.run.app"
RESPONSE=$(curl -s -w "\n%{http_code}" "$FRONTEND_URL" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is accessible"
    echo "  URL: $FRONTEND_URL"
else
    echo -e "${RED}✗${NC} Frontend not responding (HTTP $HTTP_CODE)"
fi
echo ""

# 8. Test Tour Creation
echo -e "${BLUE}🧪 Test Tour Creation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Testing orchestrator endpoint..."
ORCHESTRATOR_URL="https://tour-orchestrator-168041541697.europe-west1.run.app"

TEST_RESPONSE=$(curl -s -X POST "$ORCHESTRATOR_URL/create-tour-async" \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["history"],
    "duration": 30,
    "latitude": 48.8566,
    "longitude": 2.3522
  }' 2>/dev/null)

if echo "$TEST_RESPONSE" | grep -q "job_id"; then
    echo -e "${GREEN}✓${NC} Tour creation endpoint is working"
    JOB_ID=$(echo "$TEST_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
    echo "  Test job ID: $JOB_ID"
    
    # Wait a moment and check status
    sleep 2
    STATUS_RESPONSE=$(curl -s "$ORCHESTRATOR_URL/tour-status/$JOB_ID" 2>/dev/null)
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "  Job status: $STATUS"
else
    echo -e "${RED}✗${NC} Tour creation failed"
    echo "  Response: $TEST_RESPONSE"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📋 Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If you see any ✗ marks above, run the fix script:"
echo "  ./fix-agents-and-maps.sh"
echo ""
echo "For detailed troubleshooting, see:"
echo "  cat TROUBLESHOOTING.md"
echo ""
echo "View logs:"
echo "  gcloud logging tail 'resource.type=cloud_run_revision'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
