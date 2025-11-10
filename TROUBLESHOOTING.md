# Troubleshooting Guide

## Issues and Solutions

### 🗺️ Issue 1: Google Maps Not Showing Pinned Locations

#### Symptoms:
- Map loads but no markers appear
- Map shows blank or gray area
- Console errors about Google Maps API

#### Root Causes:
1. **API Key Issues**
   - Invalid or missing API key
   - API key not enabled for required services
   - API key restrictions blocking requests

2. **Missing Location Data**
   - Locations in Firestore don't have valid coordinates
   - Coordinates format is incorrect

#### Solutions:

##### Step 1: Verify Google Maps API Key

```bash
# Check if API key is set
echo $NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

# Or check in .env.local
cat geo-story-tours/.env.local | grep GOOGLE_MAPS
```

##### Step 2: Enable Required Google Maps APIs

Go to [Google Cloud Console](https://console.cloud.google.com/google/maps-apis) and enable:

1. **Maps JavaScript API** ✅ (Required)
2. **Places API** ✅ (Required for nearby places)
3. **Geocoding API** ✅ (Recommended)
4. **Directions API** ✅ (Recommended)

```bash
# Enable APIs via gcloud CLI
gcloud services enable maps-backend.googleapis.com
gcloud services enable places-backend.googleapis.com
gcloud services enable geocoding-backend.googleapis.com
gcloud services enable directions-backend.googleapis.com
```

##### Step 3: Check API Key Restrictions

In [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials):

1. Click on your API key
2. Under "Application restrictions":
   - For development: Choose "None"
   - For production: Choose "HTTP referrers" and add your domains
3. Under "API restrictions":
   - Choose "Restrict key"
   - Select: Maps JavaScript API, Places API, Geocoding API, Directions API
4. Save changes

##### Step 4: Verify Location Data in Firestore

```bash
# Check if locations have valid coordinates
gcloud firestore databases export gs://YOUR_BUCKET/export --collection-ids=locations

# Or use the Firebase Console
# https://console.firebase.google.com/project/durable-torus-477513-g3/firestore
```

Each location document should have:
```json
{
  "id": "location_id",
  "name": "Location Name",
  "coordinates": {
    "lat": 48.8566,
    "lng": 2.3522
  },
  "description": "...",
  "categories": ["history", "art"]
}
```

##### Step 5: Test Map Component Locally

```bash
cd geo-story-tours
npm run dev
```

Open http://localhost:3000 and check browser console for errors.

##### Step 6: Deploy with Environment Variables

```bash
# Deploy frontend with API key
gcloud run deploy geo-story-frontend \
  --source=. \
  --region=europe-west1 \
  --set-env-vars="NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_API_KEY,NEXT_PUBLIC_PROJECT_ID=durable-torus-477513-g3"
```

---

### 🤖 Issue 2: Agents Not Working

#### Symptoms:
- Tour creation hangs or times out
- "Error creating tour" message
- Agents return empty responses
- Stories not generated

#### Root Causes:
1. **Missing Gemini API Key**
2. **Firestore Permission Issues**
3. **Agent Tool Execution Failures**
4. **Cold Start Timeouts**

#### Solutions:

##### Step 1: Verify Agent Health

```bash
# Test each agent
curl https://tour-curator-agent-168041541697.europe-west1.run.app/
curl https://route-optimizer-agent-168041541697.europe-west1.run.app/
curl https://storytelling-agent-168041541697.europe-west1.run.app/
curl https://content-moderator-agent-168041541697.europe-west1.run.app/
curl https://voice-synthesis-agent-168041541697.europe-west1.run.app/

# Expected response:
# {"status":"healthy","agent":"agent_name","model":"gemini-2.5-flash","tools":X}
```

##### Step 2: Check Gemini API Key

```bash
# Verify secret exists
gcloud secrets describe gemini-api-key

# Test if agents can access the secret
gcloud secrets versions access latest --secret=gemini-api-key
```

If secret doesn't exist, create it:

```bash
# Create secret
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe durable-torus-477513-g3 --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

##### Step 3: Update Agents with API Key

```bash
# Update each agent to use the secret
for AGENT in tour-curator-agent route-optimizer-agent storytelling-agent content-moderator-agent voice-synthesis-agent; do
  gcloud run services update $AGENT \
    --region=europe-west1 \
    --update-secrets=GEMINI_API_KEY=gemini-api-key:latest
done
```

##### Step 4: Grant Firestore Permissions

```bash
# Get service account
PROJECT_NUMBER=$(gcloud projects describe durable-torus-477513-g3 --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Firestore permissions
gcloud projects add-iam-policy-binding durable-torus-477513-g3 \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/datastore.user"
```

##### Step 5: Increase Agent Timeouts

```bash
# Increase timeout for agents that need more time
gcloud run services update storytelling-agent \
  --region=europe-west1 \
  --timeout=300

gcloud run services update voice-synthesis-agent \
  --region=europe-west1 \
  --timeout=600
```

##### Step 6: Test Agent Invocation

```bash
# Test curator agent
curl -X POST https://tour-curator-agent-168041541697.europe-west1.run.app/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a tour for someone interested in history and art. Tour ID: tour_test123. Starting location: latitude 48.8566, longitude 2.3522"
  }'
```

##### Step 7: Check Agent Logs

```bash
# View logs for each agent
gcloud logging read "resource.labels.service_name=tour-curator-agent" --limit=50 --format=json

# Follow logs in real-time
gcloud logging tail "resource.type=cloud_run_revision"
```

##### Step 8: Redeploy Agents

If issues persist, redeploy all agents:

```bash
cd geo-story-tours/agents

# Deploy curator
cd curator
gcloud run deploy tour-curator-agent \
  --source=. \
  --region=europe-west1 \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Deploy optimizer
cd ../optimizer
gcloud run deploy route-optimizer-agent \
  --source=. \
  --region=europe-west1 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Deploy storyteller
cd ../storyteller
gcloud run deploy storytelling-agent \
  --source=. \
  --region=europe-west1 \
  --memory=1Gi \
  --cpu=2 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Deploy moderator
cd ../moderator
gcloud run deploy content-moderator-agent \
  --source=. \
  --region=europe-west1 \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Deploy voice synthesis
cd ../voice-synthesis
gcloud run deploy voice-synthesis-agent \
  --source=. \
  --region=europe-west1 \
  --memory=16Gi \
  --cpu=4 \
  --timeout=600 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Deploy orchestrator
cd ../orchestrator
gcloud run deploy tour-orchestrator \
  --source=. \
  --region=europe-west1 \
  --memory=1Gi \
  --cpu=1 \
  --timeout=600 \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3"
```

---

### 🔍 Common Error Messages

#### "Failed to load Google Maps API"
- **Cause**: Invalid API key or API not enabled
- **Fix**: Follow "Issue 1: Step 2" above

#### "Request timed out"
- **Cause**: Agent cold start or long processing time
- **Fix**: Increase timeout (Step 5 above) or set min-instances=1

#### "Permission denied on Firestore"
- **Cause**: Service account lacks Firestore permissions
- **Fix**: Follow "Issue 2: Step 4" above

#### "GEMINI_API_KEY not set"
- **Cause**: Secret not configured or not accessible
- **Fix**: Follow "Issue 2: Step 2-3" above

#### "No locations found"
- **Cause**: Firestore collection is empty or query filters too strict
- **Fix**: Check Firestore data and seed locations

---

### 📊 Monitoring and Debugging

#### View All Service URLs

```bash
gcloud run services list --region=europe-west1 --format="table(name,status.url)"
```

#### Check Service Logs

```bash
# All services
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# Specific service
gcloud logging read "resource.labels.service_name=tour-orchestrator" --limit=50

# Follow logs
gcloud logging tail "resource.type=cloud_run_revision"
```

#### Test End-to-End Tour Creation

```bash
# Create a test tour
curl -X POST https://tour-orchestrator-168041541697.europe-west1.run.app/create-tour-async \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["history", "art"],
    "duration": 30,
    "latitude": 48.8566,
    "longitude": 2.3522
  }'

# Response will include job_id
# Check status:
curl https://tour-orchestrator-168041541697.europe-west1.run.app/tour-status/JOB_ID
```

---

### 🚀 Quick Fix Commands

```bash
# 1. Enable all required APIs
gcloud services enable \
  maps-backend.googleapis.com \
  places-backend.googleapis.com \
  geocoding-backend.googleapis.com \
  directions-backend.googleapis.com

# 2. Grant Firestore permissions
PROJECT_NUMBER=$(gcloud projects describe durable-torus-477513-g3 --format="value(projectNumber)")
gcloud projects add-iam-policy-binding durable-torus-477513-g3 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"

# 3. Update all agents with Gemini API key
for AGENT in tour-curator-agent route-optimizer-agent storytelling-agent content-moderator-agent voice-synthesis-agent; do
  gcloud run services update $AGENT \
    --region=europe-west1 \
    --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
    --timeout=300
done

# 4. Redeploy frontend with API key
cd geo-story-tours
gcloud run deploy geo-story-frontend \
  --source=. \
  --region=europe-west1 \
  --set-env-vars="NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$(cat .env.local | grep GOOGLE_MAPS | cut -d= -f2),NEXT_PUBLIC_PROJECT_ID=durable-torus-477513-g3"
```

---

### 📞 Need More Help?

1. Check [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
2. Check [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
3. Check [Google ADK Documentation](https://cloud.google.com/agent-development-kit)
4. View project logs in [Cloud Console](https://console.cloud.google.com/logs)
