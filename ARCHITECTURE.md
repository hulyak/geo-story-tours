# Geo-Story Micro-Tours - Architecture

## System Overview

A multi-agent AI system that creates personalized city tours with AI-generated 90-second stories, deployed on Google Cloud Run.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER                                   │
│                             │                                    │
│                             ▼                                    │
│                  ┌──────────────────────┐                       │
│                  │   Frontend (Next.js)  │                       │
│                  │  Cloud Run Service    │                       │
│                  └──────────┬───────────┘                       │
│                             │                                    │
│                             ▼                                    │
│                  ┌──────────────────────┐                       │
│                  │  Tour Orchestrator    │                       │
│                  │  Cloud Run Service    │                       │
│                  │  (Coordinates Agents) │                       │
│                  └──────────┬───────────┘                       │
│                             │                                    │
│            ┌────────────────┼────────────────┐                 │
│            │                │                │                  │
│            ▼                ▼                ▼                  │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│    │Tour Curator  │  │Route Optimizer│  │Storytelling  │      │
│    │  ADK Agent   │  │   ADK Agent   │  │  ADK Agent   │      │
│    │ Cloud Run    │  │  Cloud Run    │  │  Cloud Run   │      │
│    └──────┬───────┘  └──────┬────────┘  └──────┬───────┘      │
│           │                 │                    │               │
│           └─────────────────┼────────────────────┘              │
│                             │                                    │
│                             ▼                                    │
│                  ┌──────────────────────┐                       │
│                  │Content Moderator     │                       │
│                  │    ADK Agent         │                       │
│                  │   Cloud Run          │                       │
│                  └──────────┬───────────┘                       │
│                             │                                    │
│                             ▼                                    │
│              ┌──────────────────────────────┐                  │
│              │    Google Cloud Firestore     │                  │
│              │   (Tours, Locations, Users)   │                  │
│              └───────────────────────────────┘                 │
│                                                                  │
│              ┌──────────────────────────────┐                  │
│              │    Google Cloud Pub/Sub       │                  │
│              │  (Agent Communication Bus)    │                  │
│              └───────────────────────────────┘                 │
│                                                                  │
│              ┌──────────────────────────────┐                  │
│              │       Gemini 2.0 Flash        │                  │
│              │   (All Agents use this LLM)   │                  │
│              └───────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend Layer
- **Technology**: Next.js 15, Tailwind CSS, TypeScript
- **Deployment**: Cloud Run Service
- **Function**: User interface, location browsing, tour creation
- **URL**: https://geo-story-frontend-168041541697.europe-west1.run.app

### Orchestration Layer
- **Service**: Tour Orchestrator
- **Technology**: FastAPI, Python
- **Deployment**: Cloud Run Service
- **Function**: Coordinates all AI agents in sequence
- **URL**: https://tour-orchestrator-168041541697.europe-west1.run.app
- **Workflow**:
  1. Receives tour creation requests
  2. Calls Curator → Optimizer → Storyteller → Moderator
  3. Returns complete tour with stories

### AI Agent Layer (Google ADK)

#### 1. Tour Curator Agent
- **Technology**: Google ADK `LlmAgent` + Gemini 2.0 Flash
- **Deployment**: Cloud Run Service
- **Function**:
  - Analyzes user interests
  - Queries Firestore for matching locations
  - Selects 5-8 optimal locations
  - Creates tour record
- **URL**: https://tour-curator-agent-168041541697.europe-west1.run.app
- **Tools**:
  - `query_locations_tool`: Search locations by categories
  - `create_tour_record_tool`: Save tour to Firestore
  - `publish_to_optimizer_tool`: Trigger next agent

#### 2. Route Optimizer Agent
- **Technology**: Google ADK `LlmAgent` + Gemini 2.0 Flash
- **Deployment**: Cloud Run Service
- **Function**:
  - Calculates optimal walking route
  - Uses geographic coordinates
  - Estimates travel time
  - Optimizes for efficiency
- **URL**: https://route-optimizer-agent-168041541697.europe-west1.run.app
- **Tools**:
  - `calculate_route_tool`: Optimize location order
  - `estimate_duration_tool`: Calculate timing
  - `save_route_tool`: Update Firestore

#### 3. Storytelling Agent
- **Technology**: Google ADK `LlmAgent` + Gemini 2.0 Flash
- **Deployment**: Cloud Run Service
- **Function**:
  - Generates 90-second narratives
  - Creates engaging stories per location
  - Uses historical context
  - Targets ~225 words per story
- **URL**: https://storytelling-agent-168041541697.europe-west1.run.app
- **Tools**:
  - `generate_story_tool`: Create narratives
  - `save_to_firestore_tool`: Store stories
  - `validate_length_tool`: Check word count

#### 4. Content Moderator Agent
- **Technology**: Google ADK `LlmAgent` + Gemini 2.0 Flash
- **Deployment**: Cloud Run Service
- **Function**:
  - Reviews stories for safety
  - Checks factual accuracy
  - Validates quality
  - Approves or flags content
- **URL**: https://content-moderator-agent-168041541697.europe-west1.run.app
- **Tools**:
  - `moderate_story_tool`: Evaluate content
  - `update_tour_status_tool`: Set approval status

### Data Layer

#### Firestore Database
- **Collections**:
  - `locations`: 10 curated city locations
  - `tours`: User-generated tours
  - `users`: (Future) User accounts
- **Region**: europe-west1
- **Features**: Real-time sync, offline support

#### Pub/Sub Topics
- `route-planned`: Curator → Optimizer
- `route-optimized`: Optimizer → Storyteller
- `stories-generated`: Storyteller → Moderator
- `voice-synthesis-requested`: Moderator → Voice Agent (GPU)

## Data Flow

### Tour Creation Workflow

```
1. User clicks "Create Your Tour"
   ↓
2. Frontend → Orchestrator
   POST /create-tour
   {interests: ["history"], duration: 30}
   ↓
3. Orchestrator → Curator Agent
   "Select locations for history tour"
   ↓
4. Curator queries Firestore
   Returns 6 history locations
   Saves to tours collection
   ↓
5. Orchestrator → Route Optimizer
   "Optimize route for tour_abc123"
   ↓
6. Optimizer calculates path
   Updates tour with route data
   ↓
7. Orchestrator → Storytelling Agent
   "Generate 90-sec stories"
   ↓
8. Storytelling creates narratives
   Saves stories to tour document
   ↓
9. Orchestrator → Content Moderator
   "Review and approve content"
   ↓
10. Moderator validates quality
    Sets tour status = "approved"
    ↓
11. Orchestrator → Frontend
    Returns complete tour
    ↓
12. User sees success message
    "🎉 Tour Created!"
```

## Technology Stack

### Backend Services
- **Language**: Python 3.13
- **Framework**: Google ADK (Agent Development Kit)
- **Web Framework**: FastAPI
- **LLM**: Gemini 2.0 Flash (gemini-2.0-flash-exp)
- **Deployment**: Cloud Run (serverless)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Deployment**: Cloud Run

### Google Cloud Services
- **Compute**: Cloud Run (5 services)
- **Database**: Firestore (Native mode)
- **Messaging**: Pub/Sub (4 topics)
- **AI**: Vertex AI (Gemini 2.0 Flash)
- **Secrets**: Secret Manager (API keys)

## Scalability & Performance

### Cloud Run Configuration
- **Memory**: 1-2GB per service
- **CPU**: 1 per service
- **Timeout**: 300 seconds
- **Concurrency**: 80 requests/instance
- **Autoscaling**: 0-100 instances

### Performance Optimizations
- Agent invocation: ~5-10 seconds each
- Total tour creation: ~30-40 seconds
- Caching: Firestore queries cached
- Parallel processing: Orchestrator calls agents sequentially but efficiently

## Security

- **Authentication**: Cloud Run IAM (service-to-service)
- **API Keys**: Stored in Secret Manager
- **CORS**: Configured for frontend domain
- **Firestore Rules**: Read-only for public, write for authenticated

## Future Enhancements

1. **Voice Synthesis with GPU** (L4)
   - Convert stories to audio
   - Deploy on Cloud Run with GPU
   - Real-time synthesis

2. **User Authentication**
   - Firebase Auth
   - Personal tour history
   - Saved favorites

3. **Mobile App**
   - React Native
   - GPS-guided tours
   - Offline mode

4. **Analytics**
   - BigQuery integration
   - Tour popularity tracking
   - User behavior insights

## Repository Structure

```
geo-story-tours/
├── app/                    # Next.js frontend
│   ├── page.tsx           # Main UI
│   └── api/               # API routes
├── agents/                # AI agents
│   ├── curator/          # Tour Curator
│   ├── optimizer/        # Route Optimizer
│   ├── storyteller/      # Story Generator
│   ├── moderator/        # Content Moderator
│   ├── orchestrator/     # Agent Coordinator
│   └── voice-synthesis/  # Voice Agent (GPU)
├── seed-data/            # Mock location data
└── ARCHITECTURE.md       # This file
```

## Deployment Commands

```bash
# Deploy Frontend
gcloud run deploy geo-story-frontend --source=. --region=europe-west1

# Deploy Agents
gcloud run deploy tour-curator-agent --source=agents/curator --region=europe-west1
gcloud run deploy route-optimizer-agent --source=agents/optimizer --region=europe-west1
gcloud run deploy storytelling-agent --source=agents/storyteller --region=europe-west1
gcloud run deploy content-moderator-agent --source=agents/moderator --region=europe-west1

# Deploy Orchestrator
gcloud run deploy tour-orchestrator --source=agents/orchestrator --region=europe-west1
```

## Monitoring & Logs

- **Cloud Run Logs**: Real-time agent execution logs
- **Firestore Console**: Database inspection
- **Pub/Sub Metrics**: Message flow tracking

---

**Built for Cloud Run Hackathon 2025 - AI Agents Category**
- ✅ Google ADK for multi-agent system
- ✅ Gemini 2.0 Flash for LLM
- ✅ Cloud Run for serverless deployment
- ✅ 5 coordinated services
- ✅ Real-time data with Firestore
