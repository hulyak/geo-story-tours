# 🚀 QUICKSTART - Geo-Story Micro-Tours

Get the app running in **30 minutes**!

---

## ✅ What's Fixed

All 4 AI agents now use **proper Google ADK**:
- ✅ `agents/curator/agent.py` - Tour Curator Agent
- ✅ `agents/optimizer/agent.py` - Route Optimizer Agent
- ✅ `agents/storyteller/adk_agent.py` - Storytelling Agent
- ✅ `agents/moderator/agent.py` - Content Moderator Agent

---

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
3. **Project ID**: `durable-torus-477513-g3` (or your project)
4. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🎯 30-Minute Setup

### Step 1: Enable APIs (5 min)

```bash
# Set your project
gcloud config set project durable-torus-477513-g3

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### Step 2: Create Firestore Database (2 min)

```bash
# Create Firestore database
gcloud firestore databases create --location=europe-west1

# Upload mock location data
cd seed-data
pip install google-cloud-firestore
python upload-to-firestore.py
```

**Result**: 10 sample locations uploaded ✅

### Step 3: Install ADK & Dependencies (5 min)

```bash
# Install Google ADK
pip install google-adk google-cloud-firestore google-cloud-pubsub

# Verify installation
python -c "from google.adk.agents import LlmAgent; print('✅ ADK installed')"
```

### Step 4: Setup Pub/Sub Topics (3 min)

```bash
# Create topics for agent communication
gcloud pubsub topics create route-planned
gcloud pubsub topics create route-optimized
gcloud pubsub topics create stories-generated

# Verify
gcloud pubsub topics list
```

**Result**: 3 Pub/Sub topics created ✅

### Step 5: Set Gemini API Key (2 min)

```bash
# Create secret
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to default service account
PROJECT_NUMBER=$(gcloud projects describe durable-torus-477513-g3 --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Result**: API key securely stored ✅

### Step 6: Deploy Frontend (5 min)

```bash
cd /Users/hulyakarakaya/Desktop/cloud\ run/geo-story-tours

# Deploy Next.js app
gcloud run deploy geo-story-frontend \
  --source=. \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_PROJECT_ID=durable-torus-477513-g3"
```

**Result**: Frontend live at `https://geo-story-frontend-*.run.app` ✅

### Step 7: Deploy AI Agents (8 min)

```bash
cd agents

# Deploy Tour Curator (Agent 1)
cd curator
gcloud run deploy tour-curator-agent \
  --source=. \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets="GEMINI_API_KEY=gemini-api-key:latest" \
  --memory=1Gi
cd ..

# Deploy Route Optimizer (Agent 2)
cd optimizer
gcloud run deploy route-optimizer-agent \
  --source=. \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --memory=512Mi
cd ..

# Deploy Storytelling Agent (Agent 3)
cd storyteller
gcloud run deploy storytelling-agent \
  --source=. \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets="GEMINI_API_KEY=gemini-api-key:latest" \
  --memory=1Gi \
  --cpu=2
cd ..

# Deploy Content Moderator (Agent 4)
cd moderator
gcloud run deploy content-moderator-agent \
  --source=. \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=durable-torus-477513-g3" \
  --update-secrets="GEMINI_API_KEY=gemini-api-key:latest" \
  --memory=1Gi
cd ..
```

**Result**: 4 AI agents deployed on Cloud Run ✅

---

## 🧪 Test Everything

### Test 1: Check Services

```bash
# List all services
gcloud run services list --region=europe-west1

# Should see:
# ✅ geo-story-frontend
# ✅ tour-curator-agent
# ✅ route-optimizer-agent
# ✅ storytelling-agent
# ✅ content-moderator-agent
```

### Test 2: Test Individual Agents

```bash
# Get service URLs
CURATOR_URL=$(gcloud run services describe tour-curator-agent --region=europe-west1 --format='value(status.url)')

# Test Tour Curator
curl -X POST "$CURATOR_URL/process" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a 30-minute tour focused on history and architecture",
    "context": {
      "interests": ["history", "architecture"],
      "duration": 30
    }
  }'
```

### Test 3: Test Frontend

```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe geo-story-frontend --region=europe-west1 --format='value(status.url)')

echo "🌐 Visit your app: $FRONTEND_URL"
```

Open the URL in your browser!

---

## 🎬 What Works Now

✅ **Frontend**: Browse tours, view featured content
✅ **Backend**: 4 ADK agents deployed and ready
✅ **Data**: 10 sample locations in Firestore
✅ **Infrastructure**: Pub/Sub topics created
✅ **Security**: API keys properly managed

---

## 🔧 Troubleshooting

### Issue: "Permission denied" errors

**Fix**: Grant Firestore/Pub/Sub permissions:
```bash
PROJECT_NUMBER=$(gcloud projects describe durable-torus-477513-g3 --format="value(projectNumber)")

gcloud projects add-iam-policy-binding durable-torus-477513-g3 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding durable-torus-477513-g3 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

### Issue: "google-adk not found"

**Fix**: Install in correct Python environment:
```bash
pip3 install google-adk
# or
python3 -m pip install google-adk
```

### Issue: Deployment fails with "source not found"

**Fix**: Ensure you're in the correct directory:
```bash
cd agents/curator  # Must be IN the agent directory
gcloud run deploy tour-curator-agent --source=.  # Note the dot!
```

### Issue: ADK agents not responding

**Fix**: Check agent structure:
```bash
cd agents/curator
python3 agent.py  # Should print: "✅ Tour Curator Agent initialized"
```

---

## 📊 Check Deployment Status

```bash
# View all services
gcloud run services list --region=europe-west1

# View logs from storytelling agent
gcloud logging read "resource.labels.service_name=storytelling-agent" --limit=20

# View Firestore data
gcloud firestore databases describe --database=(default)
```

---

## 🎥 Record Demo Video

Once everything works:

1. **Record Homepage** (30s)
   - Show tour browsing
   - Click categories

2. **Record Cloud Console** (1m)
   - Show 5 Cloud Run services
   - Show Pub/Sub topics
   - Show Firestore collections

3. **Record Agent Code** (30s)
   ```python
   from google.adk.agents import LlmAgent  # ← Point this out!

   storytelling_agent = LlmAgent(
       name="storytelling_agent",
       model="gemini-2.0-flash-exp",
       tools=[...]
   )
   ```

4. **Add Voiceover** using `DEMO_VIDEO_SCRIPT.md`

---

## 🏆 Hackathon Submission Checklist

- [ ] All 4 agents deployed ✅
- [ ] Frontend accessible ✅
- [ ] Mock data uploaded ✅
- [ ] Architecture diagram created
- [ ] Demo video recorded (3 min)
- [ ] Blog post written
- [ ] GitHub repo public
- [ ] Submit to hackathon platform!

---

## 🐛 Common Errors & Fixes

### Error: "Module 'google.adk' has no attribute 'agents'"

**Cause**: ADK version issue or package not installed

**Fix**:
```bash
pip install --upgrade google-adk
pip show google-adk  # Verify version >= 0.1.0
```

### Error: "Cloud Run service creation failed"

**Cause**: Billing not enabled or quotas exceeded

**Fix**:
1. Enable billing: https://console.cloud.google.com/billing
2. Check quotas: https://console.cloud.google.com/iam-admin/quotas

### Error: "GEMINI_API_KEY not set"

**Cause**: Secret not properly configured

**Fix**:
```bash
# Recreate secret
gcloud secrets delete gemini-api-key
echo -n "YOUR_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Update service
gcloud run services update storytelling-agent \
  --update-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

---

## 📚 Next Steps

1. **Test Agent Communication**: Trigger a tour creation and watch Pub/Sub messages flow
2. **Add Google Maps**: Integrate Maps API for tour visualization
3. **Polish UI**: Improve homepage design
4. **Record Demo**: Follow `DEMO_VIDEO_SCRIPT.md`
5. **Write Blog Post**: Explain your multi-agent architecture
6. **Submit to Hackathon**: Win! 🏆

---

## 💡 Quick Commands Reference

```bash
# Deploy all agents (run from agents/ directory)
for agent in curator optimizer storyteller moderator; do
  cd $agent
  gcloud run deploy ${agent}-agent --source=. --region=europe-west1 --allow-unauthenticated
  cd ..
done

# View all logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Update environment variable
gcloud run services update SERVICE_NAME --set-env-vars="KEY=VALUE"

# Delete service
gcloud run services delete SERVICE_NAME --region=europe-west1
```

---

## 🎉 You're Done!

**App is live!** Visit your frontend URL and start exploring tours.

**Questions?** Check:
- `HACKATHON_PLAN.md` for strategy
- `agents/MIGRATION_TO_ADK.md` for ADK details
- `DEMO_VIDEO_SCRIPT.md` for recording guide

**Good luck with the hackathon! 🚀**
