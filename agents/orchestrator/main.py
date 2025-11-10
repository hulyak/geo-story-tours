"""
Tour Orchestrator Service
Coordinates all AI agents to create complete tours.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
import httpx
import uvicorn
import asyncio

PORT = int(os.environ.get('PORT', 8080))
PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Agent URLs
CURATOR_URL = "https://tour-curator-agent-168041541697.europe-west1.run.app"
OPTIMIZER_URL = "https://route-optimizer-agent-168041541697.europe-west1.run.app"
STORYTELLER_URL = "https://storytelling-agent-168041541697.europe-west1.run.app"
MODERATOR_URL = "https://content-moderator-agent-168041541697.europe-west1.run.app"
VOICE_SYNTHESIS_URL = "https://voice-synthesis-agent-168041541697.europe-west1.run.app"

# Initialize Firestore
db = firestore.Client(project=PROJECT_ID)

app = FastAPI(title="Tour Orchestrator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "tour_orchestrator",
        "agents": ["curator", "optimizer", "storyteller", "moderator", "voice_synthesis"]
    }

@app.post("/create-tour")
async def create_tour(request: Request):
    """
    Orchestrate all agents to create a complete tour.

    Workflow:
    1. Curator selects locations
    2. Optimizer calculates route
    3. Storyteller generates stories
    4. Moderator approves content
    5. Voice Synthesis converts stories to audio
    """
    try:
        body = await request.json()
        interests = body.get("interests", ["history", "art"])
        duration = body.get("duration", 30)
        center_lat = body.get("latitude")
        center_lng = body.get("longitude")

        tour_id = f"tour_{uuid.uuid4().hex[:8]}"

        # Step 1: Curator - Select locations
        location_info = ""
        if center_lat is not None and center_lng is not None:
            location_info = f"\nStarting location coordinates: latitude {center_lat}, longitude {center_lng}."

        curator_prompt = f"""
        Create a personalized tour for a user interested in: {', '.join(interests)}.
        Target duration: {duration} minutes.{location_info}
        Select 5-8 locations within walking distance (5km radius) and create a tour record.
        IMPORTANT: All locations must be geographically close to each other.
        Tour ID: {tour_id}
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            curator_response = await client.post(
                f"{CURATOR_URL}/invoke",
                json={"prompt": curator_prompt}
            )
            curator_result = curator_response.json()

        # Get tour from Firestore
        tour_ref = db.collection('tours').document(tour_id)
        tour_doc = tour_ref.get()

        if not tour_doc.exists:
            # Create a mock tour if curator didn't save it
            locations_ref = db.collection('locations')
            all_locations = list(locations_ref.limit(6).stream())

            locations_data = []
            for loc_doc in all_locations:
                loc = loc_doc.to_dict()
                locations_data.append({
                    "id": loc.get("id"),
                    "name": loc.get("name"),
                    "description": loc.get("description"),
                    "coordinates": loc.get("coordinates", {"lat": 40.7128, "lng": -74.0060}),
                    "categories": loc.get("categories", []),
                    "average_visit_minutes": loc.get("average_visit_minutes", 5),
                    "image_url": loc.get("image_url")
                })

            tour_data = {
                "tour_id": tour_id,
                "interests": interests,
                "duration": duration,
                "locations": locations_data,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            tour_ref.set(tour_data)
        else:
            tour_data = tour_doc.to_dict()

        # Step 2: Route Optimizer - Calculate path
        optimizer_prompt = f"""
        Optimize the route for tour {tour_id}.
        Calculate the most efficient walking path through these locations.
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            optimizer_response = await client.post(
                f"{OPTIMIZER_URL}/invoke",
                json={"prompt": optimizer_prompt}
            )
            optimizer_result = optimizer_response.json()

        # Update tour with optimized route
        tour_ref.update({
            "optimized": True,
            "optimizer_result": str(optimizer_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Step 3: Storyteller - Generate stories
        storyteller_prompt = f"""
        Generate engaging 90-second stories for tour {tour_id}.
        Each location needs a compelling narrative.
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            storyteller_response = await client.post(
                f"{STORYTELLER_URL}/invoke",
                json={"prompt": storyteller_prompt}
            )
            storyteller_result = storyteller_response.json()

        # Update tour with stories
        tour_ref.update({
            "stories_generated": True,
            "storyteller_result": str(storyteller_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Step 4: Moderator - Approve content
        moderator_prompt = f"""
        Review and moderate the content for tour {tour_id}.
        Check for quality, safety, and appropriateness.
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            moderator_response = await client.post(
                f"{MODERATOR_URL}/invoke",
                json={"prompt": moderator_prompt}
            )
            moderator_result = moderator_response.json()

        # Update after moderation
        tour_ref.update({
            "status": "approved",
            "moderated": True,
            "moderator_result": str(moderator_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Step 5: Voice Synthesis - Convert stories to audio
        voice_synthesis_prompt = f"""
        Synthesize voice audio for all stories in tour {tour_id}.
        Use get_pending_synthesis_jobs_tool to find the stories,
        then use synthesize_voice_tool for each location,
        and update_tour_with_audio_tool to save the audio URLs.
        """

        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for audio processing
            voice_response = await client.post(
                f"{VOICE_SYNTHESIS_URL}/invoke",
                json={"prompt": voice_synthesis_prompt}
            )
            voice_result = voice_response.json()

        # Final update
        tour_ref.update({
            "status": "completed",
            "voice_synthesis_completed": True,
            "voice_synthesis_result": str(voice_result.get("response", "")),
            "completed_at": datetime.now().isoformat()
        })

        # Get final tour data
        final_tour = tour_ref.get().to_dict()

        return JSONResponse(content={
            "success": True,
            "tour_id": tour_id,
            "tour": final_tour,
            "workflow": {
                "curator": "completed",
                "optimizer": "completed",
                "storyteller": "completed",
                "moderator": "completed",
                "voice_synthesis": "completed"
            },
            "message": "Tour created successfully with AI-generated stories and voice audio!"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tours/{tour_id}")
async def get_tour(tour_id: str):
    """Get a specific tour by ID"""
    try:
        tour_ref = db.collection('tours').document(tour_id)
        tour_doc = tour_ref.get()

        if not tour_doc.exists:
            raise HTTPException(status_code=404, detail="Tour not found")

        return JSONResponse(content={
            "success": True,
            "tour": tour_doc.to_dict()
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tours")
async def list_tours():
    """List all tours"""
    try:
        tours_ref = db.collection('tours')
        tours = []

        for doc in tours_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(20).stream():
            tour_data = doc.to_dict()
            tour_data['id'] = doc.id
            tours.append(tour_data)

        return JSONResponse(content={
            "success": True,
            "count": len(tours),
            "tours": tours
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_tour_async(job_id: str, interests: List[str], duration: int, center_lat: float = None, center_lng: float = None, location_ids: List[str] = None):
    """
    Background task to process tour creation asynchronously.
    Updates job status in Firestore as it progresses.
    """
    try:
        job_ref = db.collection('jobs').document(job_id)

        tour_id = f"tour_{uuid.uuid4().hex[:8]}"

        # If user selected specific locations, use those instead of curator
        if location_ids and len(location_ids) > 0:
            # Update status: fetching user-selected locations
            job_ref.update({
                "status": "fetching_locations",
                "progress": 25,
                "updated_at": datetime.now().isoformat()
            })

            # Fetch the specific locations from Firestore
            locations_data = []
            for loc_id in location_ids:
                loc_doc = db.collection('locations').document(loc_id).get()
                if loc_doc.exists:
                    loc = loc_doc.to_dict()
                    locations_data.append({
                        "id": loc_id,
                        "name": loc.get("name"),
                        "description": loc.get("description"),
                        "coordinates": loc.get("coordinates"),
                        "categories": loc.get("categories", []),
                        "average_visit_minutes": loc.get("average_visit_minutes", 5),
                        "image_url": loc.get("image_url")
                    })

            # Create tour with user-selected locations
            tour_data = {
                "tour_id": tour_id,
                "interests": interests,
                "duration": duration,
                "locations": locations_data,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            tour_ref = db.collection('tours').document(tour_id)
            tour_ref.set(tour_data)
        else:
            # Use curator to select locations
            # Update status: curator
            job_ref.update({
                "status": "curator_running",
                "progress": 25,
                "updated_at": datetime.now().isoformat()
            })

            # Step 1: Curator
            location_info = ""
            if center_lat is not None and center_lng is not None:
                location_info = f"\nStarting location coordinates: latitude {center_lat}, longitude {center_lng}."

            curator_prompt = f"""
            Create a personalized tour for a user interested in: {', '.join(interests)}.
            Target duration: {duration} minutes.{location_info}
            Select 5-8 locations within walking distance (5km radius) and create a tour record.
            IMPORTANT: All locations must be geographically close to each other.
            Tour ID: {tour_id}
            """

            async with httpx.AsyncClient(timeout=60.0) as client:
                curator_response = await client.post(
                    f"{CURATOR_URL}/invoke",
                    json={"prompt": curator_prompt}
                )
                curator_result = curator_response.json()

            # Get tour from Firestore
            tour_ref = db.collection('tours').document(tour_id)
            tour_doc = tour_ref.get()

            if not tour_doc.exists:
                locations_ref = db.collection('locations')
                all_locations = list(locations_ref.stream())

                # Filter locations with valid coordinates only
                locations_data = []
                for loc_doc in all_locations:
                    loc = loc_doc.to_dict()
                    coords = loc.get("coordinates")

                    # Skip locations without valid coordinates
                    if not coords or not isinstance(coords, dict) or 'lat' not in coords or 'lng' not in coords:
                        continue

                    # If user location provided, calculate distance and filter
                    if center_lat and center_lng:
                        import math
                        # Haversine distance in km
                        lat1, lon1 = math.radians(center_lat), math.radians(center_lng)
                        lat2, lon2 = math.radians(coords['lat']), math.radians(coords['lng'])
                        dlat, dlon = lat2 - lat1, lon2 - lon1
                        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                        distance_km = 6371 * 2 * math.asin(math.sqrt(a))

                        # Only include locations within 10km
                        if distance_km > 10:
                            continue

                    locations_data.append({
                        "id": loc.get("id"),
                        "name": loc.get("name"),
                        "description": loc.get("description"),
                        "coordinates": coords,
                        "categories": loc.get("categories", []),
                        "average_visit_minutes": loc.get("average_visit_minutes", 5),
                        "image_url": loc.get("image_url")
                    })

                    if len(locations_data) >= 6:
                        break

                tour_data = {
                    "tour_id": tour_id,
                    "interests": interests,
                    "duration": duration,
                    "locations": locations_data,
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }
                tour_ref.set(tour_data)
            else:
                tour_data = tour_doc.to_dict()

        # Update status: optimizer
        job_ref.update({
            "status": "optimizer_running",
            "progress": 50,
            "tour_id": tour_id,
            "updated_at": datetime.now().isoformat()
        })

        # Step 2: Route Optimizer
        optimizer_prompt = f"""
        Optimize the route for tour {tour_id}.
        Calculate the most efficient walking path through these locations.
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            optimizer_response = await client.post(
                f"{OPTIMIZER_URL}/invoke",
                json={"prompt": optimizer_prompt}
            )
            optimizer_result = optimizer_response.json()

        tour_ref.update({
            "optimized": True,
            "optimizer_result": str(optimizer_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Update status: storyteller
        job_ref.update({
            "status": "storyteller_running",
            "progress": 75,
            "updated_at": datetime.now().isoformat()
        })

        # Step 3: Storyteller
        storyteller_prompt = f"""
        Please generate stories for tour_id: {tour_id}
        
        Instructions:
        1. Fetch the tour data using get_tour_tool("{tour_id}")
        2. Generate a unique, engaging 90-second story for each location
        3. Save all stories using generate_and_save_stories_tool
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            storyteller_response = await client.post(
                f"{STORYTELLER_URL}/invoke",
                json={"prompt": storyteller_prompt}
            )
            storyteller_result = storyteller_response.json()

        tour_ref.update({
            "stories_generated": True,
            "storyteller_result": str(storyteller_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Update status: moderator
        job_ref.update({
            "status": "moderator_running",
            "progress": 90,
            "updated_at": datetime.now().isoformat()
        })

        # Step 4: Moderator
        moderator_prompt = f"""
        Please review and moderate tour_id: {tour_id}
        
        Instructions:
        1. Fetch the tour using get_tour_tool("{tour_id}")
        2. Review all stories for quality, safety, and appropriateness
        3. Use moderate_content_tool to approve or flag issues
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            moderator_response = await client.post(
                f"{MODERATOR_URL}/invoke",
                json={"prompt": moderator_prompt}
            )
            moderator_result = moderator_response.json()

        tour_ref.update({
            "status": "approved",
            "moderated": True,
            "moderator_result": str(moderator_result.get("response", "")),
            "updated_at": datetime.now().isoformat()
        })

        # Update status: voice synthesis
        job_ref.update({
            "status": "voice_synthesis_running",
            "progress": 95,
            "updated_at": datetime.now().isoformat()
        })

        # Step 5: Voice Synthesis
        voice_synthesis_prompt = f"""
        Please synthesize voice audio for tour_id: {tour_id}
        
        Instructions:
        1. Use get_pending_synthesis_jobs_tool to find stories that need audio
        2. For each story, use synthesize_voice_tool to create audio
        3. Use update_tour_with_audio_tool to save the audio URLs to Firestore
        """

        async with httpx.AsyncClient(timeout=120.0) as client:
            voice_response = await client.post(
                f"{VOICE_SYNTHESIS_URL}/invoke",
                json={"prompt": voice_synthesis_prompt}
            )
            voice_result = voice_response.json()

        tour_ref.update({
            "status": "completed",
            "voice_synthesis_completed": True,
            "voice_synthesis_result": str(voice_result.get("response", "")),
            "completed_at": datetime.now().isoformat()
        })

        # Final update: completed
        final_tour = tour_ref.get().to_dict()
        job_ref.update({
            "status": "completed",
            "progress": 100,
            "tour_id": tour_id,
            "tour": final_tour,
            "completed_at": datetime.now().isoformat()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        # Update job with error
        job_ref = db.collection('jobs').document(job_id)
        job_ref.update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.now().isoformat()
        })

@app.post("/create-tour-async")
async def create_tour_async(request: Request, background_tasks: BackgroundTasks):
    """
    Start tour creation asynchronously and return immediately.
    Returns a job_id that can be used to check status.
    """
    try:
        body = await request.json()
        interests = body.get("interests", ["history", "art"])
        duration = body.get("duration", 30)
        center_lat = body.get("latitude")
        center_lng = body.get("longitude")
        location_ids = body.get("location_ids", [])

        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create job record
        job_ref = db.collection('jobs').document(job_id)
        job_ref.set({
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "interests": interests,
            "duration": duration,
            "latitude": center_lat,
            "longitude": center_lng,
            "location_ids": location_ids,
            "created_at": datetime.now().isoformat()
        })

        # Add background task
        background_tasks.add_task(process_tour_async, job_id, interests, duration, center_lat, center_lng, location_ids)

        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": "Tour creation started. Use /tour-status/{job_id} to check progress."
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tour-status/{job_id}")
async def get_tour_status(job_id: str):
    """
    Check the status of an async tour creation job.
    """
    try:
        job_ref = db.collection('jobs').document(job_id)
        job_doc = job_ref.get()

        if not job_doc.exists:
            raise HTTPException(status_code=404, detail="Job not found")

        job_data = job_doc.to_dict()

        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "status": job_data.get("status"),
            "progress": job_data.get("progress", 0),
            "tour_id": job_data.get("tour_id"),
            "tour": job_data.get("tour"),
            "error": job_data.get("error"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "completed_at": job_data.get("completed_at")
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"🚀 Starting Tour Orchestrator on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
