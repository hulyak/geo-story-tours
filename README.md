# 📖 PocketGuide

> Audio tour platform using 5 specialized agents to create personalized walking tours with 90-second stories and GPU-accelerated voice synthesis.

![Status](https://img.shields.io/badge/status-ready-success) ![ADK](https://img.shields.io/badge/Google_ADK-✓-blue) ![Cloud Run](https://img.shields.io/badge/Cloud_Run-7_services-orange) ![GPU](https://img.shields.io/badge/GPU-L4-green)

## 🚀 Quick Start

```bash
# 1. Clone & setup (5 min)
git clone https://github.com/hulyak/geo-story-tours.git
cd geo-story-tours

# 2. Follow detailed guide
cat QUICKSTART.md

# 3. Deploy everything (30 min)
# See QUICKSTART.md for step-by-step
```

**Result**: App live at `https://your-app.run.app` ✅

---

## 📂 Project Structure

```
geo-story-tours/
├── app/                          # Next.js frontend
│   ├── page.tsx                 # Homepage with tour browsing & creation
│   ├── api/locations/route.ts  # Server-side Firestore API
│   └── layout.tsx               # App layout
│
├── agents/                       # Google ADK Agents
│   ├── orchestrator/            # 🆕 Tour Orchestrator
│   │   ├── main.py              # Coordinates all agents
│   │   └── requirements.txt
│   ├── curator/
│   │   ├── agent.py             # ✅ ADK LlmAgent
│   │   └── main.py              # FastAPI wrapper
│   ├── optimizer/
│   │   ├── agent.py             # ✅ ADK LlmAgent
│   │   └── main.py              # FastAPI wrapper
│   ├── storyteller/
│   │   ├── agent.py             # ✅ ADK LlmAgent
│   │   └── main.py              # FastAPI wrapper
│   ├── moderator/
│   │   ├── agent.py             # ✅ ADK LlmAgent
│   │   └── main.py              # FastAPI wrapper
│   └── voice-synthesis/         # 🆕 Voice Agent
│       ├── agent.py             # ✅ ADK LlmAgent
│       ├── main.py              # FastAPI wrapper
│       ├── Dockerfile           # Standard Python base image
│       └── requirements.txt
│
├── seed-data/
│   ├── locations.json           # 10 sample locations
│   └── upload-via-rest.sh       # Upload script
│
└── README.md                    # This file
```

---

## 🎨 Features

### Production Ready (Live)
- ✅ **Frontend**: Modern UI with tour browsing and filtering
  - URL: https://geo-story-tours-168041541697.europe-west1.run.app/
  - Working "Create Your Tour" button
  - Real-time progress indicator
  - Category filtering (history, art, food, hidden gems)

- ✅ **Tour Orchestrator**: Coordinates all AI agents
  - URL: https://tour-orchestrator-168041541697.europe-west1.run.app
  - Sequential agent execution (Curator → Optimizer → Storyteller → Moderator)
  - Complete multi-agent workflow

- ✅ **5 ADK Agents**: All deployed on Cloud Run
  - All use Google ADK `LlmAgent` class
  - All use Gemini 2.5 Flash model
  - Tour Curator, Route Optimizer, Storytelling, Content Moderator

- ✅ **GPU Voice Synthesis**: L4 GPU-accelerated audio generation
  - URL: https://voice-synthesis-agent-168041541697.us-central1.run.app
  - Real-time 90-second story → audio conversion
  - 16Gi memory, 4 CPUs, 1x NVIDIA L4 GPU

- ✅ **Architecture Documentation**: Complete ARCHITECTURE.md
  - ASCII architecture diagrams
  - Component breakdown for all 7 services
  - Data flow documentation
  - Deployment commands

- ✅ **10 Sample Locations**: Seeded in Firestore
  - Historic City Hall, Caffe Angelo, Hidden Alleyway Mural, etc.

### In Progress
-  Integrate voice synthesis into tour creation flow
- Google Maps integration
- 🚧 Tour detail pages with audio playback
- 🚧 User authentication

 Database Information:
  - Type: Google Cloud Firestore (NoSQL, serverless)
  - Current: 10 locations in New York area
  - Scalability: Can handle millions of locations
  - Cost: Free tier covers 50K reads/day
  - Structure: Each location has id, name, coordinates (lat/lng), categories, description,
  etc.
  
### Planned
- 📅 Offline tour downloads
- 📅 Creator revenue sharing
- 📅 Social sharing & badges
- 📅 Mobile app

## 🧪 Local Development

```bash
# Install dependencies
npm install
pip install google-adk google-cloud-firestore google-cloud-pubsub

# Run frontend
npm run dev
# Visit http://localhost:3001

# Test agent locally
cd agents/storyteller
python adk_agent.py
```

---

## 📊 Monitoring

```bash
# View all services
gcloud run services list --region=europe-west1

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# View Firestore data
gcloud firestore databases describe --database=(default)

# View Pub/Sub topics
gcloud pubsub topics list
```

---

## 🐛 Troubleshooting

See `QUICKSTART.md` for detailed troubleshooting guide.

**Common Issues**:
- "google-adk not found" → `pip install google-adk`
- "Permission denied" → Grant Firestore/Pub/Sub IAM roles
- "GEMINI_API_KEY not set" → Recreate secret in Secret Manager

---

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)**: 30-minute setup guide
- **[agents/README.md](./agents/README.md)**: Agent-specific documentation


## 📝 License

MIT License - feel free to use for your own projects!


## 🎉 Quick Commands

```bash
# Deploy everything
cd geo-story-tours
./QUICKSTART.md  # Follow step-by-step

# Update agent
cd agents/storyteller
gcloud run deploy storytelling-agent --source=.

# View logs
gcloud logging read "resource.labels.service_name=storytelling-agent" --limit=20

# Test agent
AGENT_URL=$(gcloud run services describe storytelling-agent --region=europe-west1 --format='value(status.url)')
curl -X POST "$AGENT_URL/process" -H "Content-Type: application/json" -d '{"input":"Generate a story"}'
```
