# AI Agents - Geo-Story Micro-Tours

This directory contains 4 AI agents built with Python and Flask, designed to run on Google Cloud Run and communicate via Pub/Sub.

## 🤖 The 4 Agents

### 1. Tour Curator Agent (`curator/`)
**Port**: 8080
**Endpoint**: `/curate`

**Purpose**: Analyzes user preferences and selects optimal locations for a personalized tour.

**What it does**:
- Uses Gemini to understand user interests
- Queries Firestore for matching locations
- Selects 5-8 points of interest
- Creates initial tour structure
- Publishes to `route-planned` Pub/Sub topic

**Request Example**:
```bash
curl -X POST http://localhost:8080/curate \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "interests": ["history", "architecture"],
      "duration": 30,
      "accessibility": ["wheelchair_accessible"]
    },
    "start_location": {"lat": 40.7128, "lng": -74.0060}
  }'
```

---

### 2. Route Optimizer Agent (`optimizer/`)
**Port**: 8083
**Endpoint**: `/optimize`

**Purpose**: Calculates optimal walking paths between locations.

**What it does**:
- Receives location list from Tour Curator
- Uses Haversine formula to calculate distances
- Applies nearest-neighbor algorithm for route optimization
- Estimates walking time (80 meters/minute average)
- Publishes to `route-optimized` Pub/Sub topic

**Key Algorithm**:
```python
# Nearest neighbor TSP approximation
while locations_remaining:
    nearest = find_closest(current_position, locations_remaining)
    add_to_route(nearest)
    current_position = nearest.coordinates
```

---

### 3. Storytelling Agent (`storyteller/`)
**Port**: 8081
**Endpoint**: `/generate-story`

**Purpose**: Generates engaging 90-second narratives using Gemini 2.0 Flash.

**What it does**:
- Receives optimized route from Route Optimizer
- For each location, uses Gemini to generate a compelling 90-second story
- Adapts tone based on audience (family-friendly, historical, local-secrets)
- Ensures stories are ~225 words (90s at 2.5 words/second)
- Publishes to `stories-generated` Pub/Sub topic

**Story Structure**:
```
Hook (5-10s): "Stop here. Right here. Do you feel it?"
Body (70-75s): Blend historical facts with emotional storytelling
Closing (5-10s): Connect to present or next location
```

**Gemini Prompt Example**:
```python
prompt = f"""
Generate a captivating 90-second story for:
Location: {location.name}
Audience: {audience}
Theme: {tour_theme}

Use vivid language, surprising facts, present tense.
Target: ~225 words
"""
```

---

### 4. Content Moderator Agent (`moderator/`)
**Port**: 8082
**Endpoint**: `/moderate`

**Purpose**: Reviews stories for quality, safety, and accuracy.

**What it does**:
- Receives tour with stories from Storytelling Agent
- Uses Gemini to evaluate each story on:
  - Content safety (appropriate for all audiences?)
  - Factual accuracy (plausible historical/cultural facts?)
  - Quality (engaging and well-written?)
  - Tone (respectful and appropriate?)
- Saves approved tours to Firestore with status `approved`
- Flags problematic content for human review

**Moderation Response**:
```json
{
  "approved": true,
  "safety_score": 95,
  "quality_score": 90,
  "issues": [],
  "suggestions": ["Could add more sensory details"],
  "reasoning": "High-quality, factually accurate, appropriate tone"
}
```

---

## 🔄 Agent Communication Flow

```
User Request
    ↓
[Tour Curator Agent]
    ↓ Pub/Sub: route-planned
[Route Optimizer Agent]
    ↓ Pub/Sub: route-optimized
[Storytelling Agent] ← Gemini 2.0 Flash
    ↓ Pub/Sub: stories-generated
[Content Moderator Agent] ← Gemini validation
    ↓
Firestore: Approved Tour
    ↓
Frontend displays tour
```

---

## 🚀 Deployment

### Quick Deploy (All Agents)

```bash
cd agents
./deploy-all.sh
```

This will:
1. Deploy all 4 agents to Cloud Run
2. Configure memory and CPU resources
3. Set environment variables
4. Enable auto-scaling (0-10 instances)

### Setup Pub/Sub Communication

```bash
cd ..
./setup-pubsub.sh
```

This creates:
- 3 Pub/Sub topics (`route-planned`, `route-optimized`, `stories-generated`)
- Push subscriptions to trigger each agent
- Automatic message routing

### Test Agents

```bash
cd agents
./test-agents.sh
```

This tests:
- Health checks for all agents
- Tour curation
- Route optimization
- Story generation
- Content moderation

---

## 🧪 Local Development

### Run Agent Locally

```bash
# 1. Set environment variables
export PROJECT_ID=durable-torus-477513-g3
export GEMINI_API_KEY=your_api_key
export PORT=8080

# 2. Install dependencies
cd curator
pip install -r requirements.txt

# 3. Run
python src/main.py
```

### Test Locally

```bash
# Test Tour Curator
curl http://localhost:8080/ # Health check
curl -X POST http://localhost:8080/curate -H "Content-Type: application/json" -d @test-data/tour-request.json

# Test Storytelling Agent
curl -X POST http://localhost:8081/generate-story -H "Content-Type: application/json" -d @test-data/story-request.json
```

---

## 📊 Resource Configuration

### Tour Curator Agent
- **Memory**: 1Gi
- **CPU**: 1
- **Scaling**: 0-10 instances
- **Reason**: Needs memory for Gemini API calls and Firestore queries

### Route Optimizer Agent
- **Memory**: 512Mi
- **CPU**: 1
- **Scaling**: 0-10 instances
- **Reason**: Lightweight calculations, no AI model

### Storytelling Agent
- **Memory**: 1Gi
- **CPU**: 2
- **Scaling**: 0-5 instances
- **Reason**: Gemini API calls are CPU-intensive, needs parallel processing

### Content Moderator Agent
- **Memory**: 1Gi
- **CPU**: 1
- **Scaling**: 0-10 instances
- **Reason**: Gemini validation, moderate load

---

## 🔐 Secrets Management

### Set Gemini API Key

```bash
# Create secret
echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to service accounts
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update agents to use secret
gcloud run services update storytelling-agent \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

gcloud run services update tour-curator-agent \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest

gcloud run services update content-moderator-agent \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest
```

---

## 🐛 Debugging

### View Logs

```bash
# All agents
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json

# Specific agent
gcloud logging read "resource.labels.service_name=storytelling-agent" --limit=20

# Follow logs in real-time
gcloud logging tail "resource.type=cloud_run_revision"
```

### Common Issues

**Issue**: Agent timeout on Pub/Sub messages
**Solution**: Increase timeout in Cloud Run config:
```bash
gcloud run services update storytelling-agent --timeout=300
```

**Issue**: Gemini API quota exceeded
**Solution**: Check API limits in GCP Console → APIs & Services → Gemini API

**Issue**: Pub/Sub messages not triggering agents
**Solution**: Check subscription configuration:
```bash
gcloud pubsub subscriptions describe route-optimized-sub
```

---

## 📈 Monitoring

### Key Metrics to Watch

1. **Request Latency**:
   - Curator: <2s
   - Optimizer: <1s
   - Storyteller: 5-15s (Gemini calls are slow)
   - Moderator: 3-8s

2. **Instance Count**:
   - Should scale to 0 when idle
   - Should auto-scale up under load

3. **Error Rate**:
   - Target: <1%
   - Main causes: Gemini API errors, Firestore timeouts

### Dashboard Query

```
resource.type="cloud_run_revision"
resource.labels.service_name=~".*-agent"
severity>=WARNING
```

---

## 🎯 Performance Optimization

### Caching

```python
# Cache Firestore queries
from functools import lru_cache

@lru_cache(maxsize=100)
def get_locations_by_category(category):
    return firestore_client.collection('locations').where('category', '==', category).get()
```

### Batch Processing

```python
# Generate multiple stories in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    stories = list(executor.map(generate_story, locations))
```

### Reduce Cold Starts

```bash
# Set minimum instances to 1 for critical agents
gcloud run services update storytelling-agent --min-instances=1
```

---

## 🏆 Hackathon Demo Tips

### Show Agent Orchestration

1. **Open Cloud Console**: Pub/Sub → Topics
2. **Trigger a tour**: `curl -X POST $CURATOR_URL/curate ...`
3. **Watch messages flow**:
   - `route-planned` → message appears
   - `route-optimized` → message appears
   - `stories-generated` → message appears
4. **Show Firestore**: Document updates in real-time

### Demo Script

"Here's what makes this special. Watch as 4 AI agents collaborate:

1. **Tour Curator** analyzes your preferences with Gemini
2. **Route Optimizer** calculates the perfect walking path
3. **Storytelling Agent** uses Gemini to write 6 unique 90-second stories
4. **Content Moderator** validates everything is accurate and appropriate

All happening in real-time, fully serverless on Cloud Run, communicating through Pub/Sub. This is true multi-agent AI."

---

## 📚 Additional Resources

- [Agent Development Kit Docs](https://cloud.google.com/agent-development-kit)
- [Gemini API Guide](https://ai.google.dev/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Pub/Sub Best Practices](https://cloud.google.com/pubsub/docs/best-practices)

---

## 🤝 Contributing

Found a bug or want to improve an agent? PRs welcome!

1. Fork the repo
2. Create your feature branch
3. Test locally
4. Submit PR with clear description

---

**Built for Cloud Run Hackathon 2025 - AI Agents Category** 🏆
