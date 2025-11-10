# Deployment Guide

## Prerequisites

1. Google Cloud Project with billing enabled
2. Google Maps API key with required APIs enabled
3. gcloud CLI installed and authenticated

## Required Google Cloud APIs

Enable these APIs in your project:

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  maps-backend.googleapis.com \
  places-backend.googleapis.com \
  geocoding-backend.googleapis.com \
  directions-backend.googleapis.com
```

## Google Maps API Key Setup

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an API key or use existing one
3. Configure API restrictions:
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Directions API
4. Configure application restrictions:
   - For testing: Set to "None"
   - For production: Add your Cloud Run URL as HTTP referrer

## Gemini API Key Setup

```bash
# Create secret for Gemini API key
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Deploy Frontend

```bash
# Set your environment variables
export PROJECT_ID="your-project-id"
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key"
export REGION="europe-west1"

# Deploy frontend with environment variables
gcloud run deploy geo-story-tours \
  --source=. \
  --region=$REGION \
  --project=$PROJECT_ID \
  --update-env-vars="NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY,NEXT_PUBLIC_PROJECT_ID=$PROJECT_ID" \
  --allow-unauthenticated
```

## Deploy Agents

```bash
# Deploy all agents
cd agents

# Tour Curator
cd curator
gcloud run deploy tour-curator-agent \
  --source=. \
  --region=$REGION \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

# Route Optimizer
cd ../optimizer
gcloud run deploy route-optimizer-agent \
  --source=. \
  --region=$REGION \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

# Storytelling Agent
cd ../storyteller
gcloud run deploy storytelling-agent \
  --source=. \
  --region=$REGION \
  --memory=1Gi \
  --cpu=2 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

# Content Moderator
cd ../moderator
gcloud run deploy content-moderator-agent \
  --source=. \
  --region=$REGION \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated

# Voice Synthesis
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

# Tour Orchestrator
cd ../orchestrator
gcloud run deploy tour-orchestrator \
  --source=. \
  --region=$REGION \
  --memory=1Gi \
  --cpu=1 \
  --timeout=600 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID" \
  --allow-unauthenticated
```

## Seed Location Data

```bash
cd seed-data
python3 upload-to-firestore.py
```

## Verify Deployment

```bash
# Check all services
gcloud run services list --region=$REGION

# Test frontend
curl https://YOUR_FRONTEND_URL

# Test agents
curl https://YOUR_AGENT_URL/
```

## Environment Variables

### Frontend (geo-story-tours)
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` - Google Maps API key
- `NEXT_PUBLIC_PROJECT_ID` - Google Cloud project ID

### Agents (all)
- `PROJECT_ID` - Google Cloud project ID
- `GEMINI_API_KEY` - Gemini API key (from Secret Manager)

## Security Notes

1. **Never commit API keys** to git
2. Use `.env.local` for local development (already in .gitignore)
3. Use Secret Manager for sensitive keys in production
4. Restrict API keys to specific APIs and domains
5. Enable Cloud Run authentication for production

## Troubleshooting

### Google Maps not loading
- Check API key is set correctly
- Verify API restrictions allow your domain
- Check browser console for specific error

### Agents not responding
- Check logs: `gcloud logging tail 'resource.type=cloud_run_revision'`
- Verify Gemini API key secret is accessible
- Check Firestore permissions

### Stories not generating
- Verify storytelling agent is deployed
- Check agent logs for errors
- Ensure Gemini API quota is not exceeded

## Cost Optimization

- Set `--min-instances=0` for all services (default)
- Use `--max-instances=10` to cap scaling
- Monitor usage in Cloud Console
- Consider Cloud Run free tier limits

## Support

For issues, check:
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `ARCHITECTURE.md` - System architecture
- Cloud Run logs - Real-time error logs
