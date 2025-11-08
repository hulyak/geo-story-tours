# Worker Pools and Background Jobs

This directory contains background workers and batch processing jobs as described in JOBS_AND_WORKERS.md.

## Architecture Overview

```
User Request → Tour Orchestrator → Cloud Tasks Queue → Background Workers
                                 ↓
                              Pub/Sub Topics → Event-Driven Workers
                                 ↓
                            Cloud Scheduler → Periodic Jobs
```

## Available Workers

### 1. Analytics Aggregation Worker
**File**: `analytics-aggregation.py`
**Purpose**: Calculate tour popularity, rating trends, and user metrics
**Schedule**: Daily at midnight UTC
**Resources**: 1 CPU, 1GB RAM

**What it does**:
- Counts total tours created
- Calculates average tour duration
- Identifies top 10 most popular locations
- Aggregates user feedback and ratings
- Stores results in Firestore `analytics` collection

### 2. Voice Synthesis Batch Worker
**File**: `voice-synthesis-batch.py`
**Purpose**: Process audio generation for tours using GPU
**Schedule**: Every 5 minutes
**Resources**: 4 CPU, 16GB RAM, 1x NVIDIA L4 GPU

**What it does**:
- Finds tours with `audio_status: 'pending'`
- Processes up to 10 tours per batch
- Generates audio for each location's story
- Uploads audio to Cloud Storage
- Updates Firestore with audio URLs

## Infrastructure

### Cloud Tasks Queues
```bash
# Tour creation queue
tour-creation-queue
  Max attempts: 3
  Max concurrent: 100
  Region: europe-west1
```

### Pub/Sub Topics
```bash
# Voice synthesis events
tour-voice-synthesis
  Subscription: tour-voice-synthesis-sub

# Story regeneration (low ratings)
story-regeneration
  Subscription: story-regeneration-sub

# Content moderation flags
content-moderation
  Subscription: content-moderation-sub
```

### Cloud Scheduler Jobs
```bash
# Analytics - Daily at midnight
analytics-cron
  Schedule: 0 0 * * * (daily 00:00 UTC)
  Target: analytics-worker job

# Voice Synthesis - Every 5 minutes
voice-synthesis-cron
  Schedule: */5 * * * * (every 5 min)
  Target: voice-synthesis-worker job
```

## Deployment

### 1. Deploy Workers
```bash
cd workers
./deploy-workers.sh
```

This will:
- Build Docker images for both workers
- Deploy to Cloud Run Jobs
- Configure resources (CPU, RAM, GPU)

### 2. Setup Schedulers
```bash
./setup-scheduler.sh
```

This will:
- Create Cloud Scheduler jobs
- Link to Cloud Run Jobs
- Set cron schedules

### 3. Verify Deployment
```bash
# Check Cloud Run Jobs
gcloud run jobs list --region=europe-west1
gcloud run jobs list --region=us-central1

# Check Cloud Scheduler
gcloud scheduler jobs list --location=europe-west1
gcloud scheduler jobs list --location=us-central1

# Check Pub/Sub topics
gcloud pubsub topics list

# Check Cloud Tasks queues
gcloud tasks queues list --location=europe-west1
```

## Manual Execution

### Run Analytics Worker
```bash
gcloud run jobs execute analytics-worker --region=europe-west1
```

### Run Voice Synthesis Worker
```bash
gcloud run jobs execute voice-synthesis-worker --region=us-central1
```

### Trigger via Scheduler
```bash
gcloud scheduler jobs run analytics-cron --location=europe-west1
gcloud scheduler jobs run voice-synthesis-cron --location=us-central1
```

## Monitoring

### View Job Executions
```bash
# List recent executions
gcloud run jobs executions list --job=analytics-worker --region=europe-west1
gcloud run jobs executions list --job=voice-synthesis-worker --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_job" --limit=50
```

### Check Queue Status
```bash
# View Cloud Tasks queue
gcloud tasks queues describe tour-creation-queue --location=europe-west1

# View Pub/Sub backlog
gcloud pubsub subscriptions describe tour-voice-synthesis-sub
```

## Cost Estimates (Monthly)

Based on JOBS_AND_WORKERS.md projections:

| Worker | Frequency | Monthly Cost |
|--------|-----------|--------------|
| Analytics Aggregation | Daily | $0.20 |
| Voice Synthesis (GPU) | Every 5 min | $173 |
| Story Regeneration | On-demand | $1 |
| **Total** | | **~$174/month** |

## Adding New Workers

1. Create worker script in this directory
2. Add Dockerfile
3. Update `deploy-workers.sh`
4. Add scheduler in `setup-scheduler.sh` if periodic
5. Document in this README

## Environment Variables

Workers automatically get these from Cloud Run:

- `GOOGLE_CLOUD_PROJECT` - Project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Auto-configured

Additional variables can be set:
- `AUDIO_STORAGE_BUCKET` - Bucket for audio files
- `MAX_BATCH_SIZE` - Max tours per batch

## Troubleshooting

### Worker Fails
```bash
# Check logs
gcloud run jobs executions describe EXECUTION_ID --region=REGION

# View detailed logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=analytics-worker" --limit=100
```

### Queue Backing Up
```bash
# Check queue size
gcloud tasks queues describe tour-creation-queue --location=europe-west1

# Pause queue
gcloud tasks queues pause tour-creation-queue --location=europe-west1

# Resume queue
gcloud tasks queues resume tour-creation-queue --location=europe-west1
```

### GPU Not Available
Voice synthesis worker requires L4 GPU in us-central1. If unavailable:
- Try different region (us-west1, europe-west4)
- Use T4 GPU instead: `--gpu-type=nvidia-t4`
- Increase retry attempts

## References

- [JOBS_AND_WORKERS.md](../JOBS_AND_WORKERS.md) - Full specifications
- [Cloud Run Jobs Docs](https://cloud.google.com/run/docs/create-jobs)
- [Cloud Scheduler Docs](https://cloud.google.com/scheduler/docs)
- [Cloud Tasks Docs](https://cloud.google.com/tasks/docs)
