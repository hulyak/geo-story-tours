# Repository Structure

## 📁 Project Organization

```
geo-story-tours/
├── app/                          # Next.js frontend application
│   ├── components/              # React components
│   │   ├── TourMap.tsx         # Google Maps integration
│   │   ├── AnalyticsDashboard.tsx
│   │   ├── TourRating.tsx
│   │   └── NearbyPlaces.tsx
│   ├── tours/                   # Tour pages
│   │   ├── [tourId]/           # Tour detail page
│   │   └── status/[jobId]/     # Tour creation status
│   ├── utils/                   # Utility functions
│   │   ├── routeOptimization.ts
│   │   └── tourExport.ts
│   ├── api/                     # API routes
│   │   └── locations/          # Locations API
│   └── page.tsx                # Homepage
│
├── agents/                      # AI Agents (Google ADK)
│   ├── curator/                # Tour Curator Agent
│   │   ├── agent.py           # ADK agent definition
│   │   ├── main.py            # FastAPI wrapper
│   │   └── Dockerfile
│   ├── optimizer/              # Route Optimizer Agent
│   ├── storyteller/            # Storytelling Agent
│   ├── moderator/              # Content Moderator Agent
│   ├── voice-synthesis/        # Voice Synthesis Agent
│   └── orchestrator/           # Tour Orchestrator
│
├── seed-data/                   # Initial data
│   ├── locations.json          # 25 Paris locations
│   ├── upload-to-firestore.py  # Upload script
│   └── upload-via-rest.sh      # Alternative upload
│
├── public/                      # Static assets
│
├── .env.example                 # Environment variables template
├── .env.local                   # Local environment (gitignored)
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Project overview
├── ARCHITECTURE.md              # System architecture
├── DEPLOYMENT.md                # Deployment instructions
├── QUICKSTART.md                # Quick setup guide
├── TROUBLESHOOTING.md           # Common issues & solutions
├── ADDING_LOCATIONS.md          # How to add locations
│
├── diagnose.sh                  # System health checker
├── setup-pubsub.sh              # Pub/Sub setup
│
├── package.json                 # Node dependencies
├── tsconfig.json                # TypeScript config
├── tailwind.config.ts           # Tailwind CSS config
└── next.config.js               # Next.js config
```

## 📄 Key Files

### Documentation
- **README.md** - Project overview and features
- **ARCHITECTURE.md** - System design and data flow
- **DEPLOYMENT.md** - Step-by-step deployment guide
- **QUICKSTART.md** - Quick 30-minute setup
- **TROUBLESHOOTING.md** - Common issues and fixes
- **ADDING_LOCATIONS.md** - How to add new locations

### Configuration
- **.env.example** - Environment variables template
- **.env.local** - Local development config (not in git)
- **package.json** - Frontend dependencies
- **tsconfig.json** - TypeScript configuration
- **tailwind.config.ts** - Styling configuration

### Scripts
- **diagnose.sh** - Check system health and identify issues
- **setup-pubsub.sh** - Configure Pub/Sub topics

### Data
- **seed-data/locations.json** - 25 curated Paris locations
- **seed-data/upload-to-firestore.py** - Upload locations to Firestore

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd geo-story-tours
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API keys
   ```

3. **Install dependencies**
   ```bash
   npm install
   ```

4. **Run locally**
   ```bash
   npm run dev
   ```

5. **Deploy to Cloud Run**
   ```bash
   # See DEPLOYMENT.md for full instructions
   ```

## 📚 Documentation Guide

- **New to the project?** Start with `README.md`
- **Want to deploy?** Follow `DEPLOYMENT.md`
- **Need quick setup?** Use `QUICKSTART.md`
- **Having issues?** Check `TROUBLESHOOTING.md`
- **Want to understand the system?** Read `ARCHITECTURE.md`
- **Adding locations?** See `ADDING_LOCATIONS.md`

## 🔧 Maintenance

### Health Check
```bash
./diagnose.sh
```

### View Logs
```bash
gcloud logging tail 'resource.type=cloud_run_revision'
```

### Update Agents
```bash
cd agents/<agent-name>
gcloud run deploy <agent-name> --source=.
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check `TROUBLESHOOTING.md`
2. Run `./diagnose.sh`
3. Check Cloud Run logs
4. Review documentation

## 🔒 Security

- Never commit API keys
- Use `.env.local` for secrets (gitignored)
- Use Secret Manager in production
- Restrict API keys to specific domains
