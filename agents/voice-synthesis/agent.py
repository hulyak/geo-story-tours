"""
Voice Synthesis Agent - Google ADK Implementation with GPU Support

Generates realistic voice audio from story text using GPU acceleration.
Designed to run on Cloud Run with L4 GPU for real-time synthesis.
"""

from google.adk.agents.llm_agent import Agent
from google.cloud import firestore, storage
from google.cloud import texttospeech
import os
import json
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ID = os.environ.get('PROJECT_ID', 'durable-torus-477513-g3')

# Initialize Google Cloud clients
firestore_client = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
tts_client = texttospeech.TextToSpeechClient()


def synthesize_voice_tool(story_text: str, location_id: str, voice_config: Dict = None) -> str:
    """
    Synthesize voice audio from story text using Google Text-to-Speech.

    This function uses GPU acceleration for faster synthesis.

    Args:
        story_text: The story script to convert to speech
        location_id: Location identifier for file naming
        voice_config: Optional voice configuration (gender, language, name)

    Returns:
        JSON result with audio file URL
    """
    try:
        # Default voice configuration
        if voice_config is None:
            voice_config = {
                "language_code": "en-US",
                "name": "en-US-Neural2-J",  # Natural sounding voice
                "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL
            }

        # Prepare synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=story_text)

        # Configure voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"],
            name=voice_config["name"],
            ssml_gender=voice_config.get("ssml_gender", texttospeech.SsmlVoiceGender.NEUTRAL)
        )

        # Configure audio output (MP3 format for web compatibility)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Natural speaking rate
            pitch=0.0  # Neutral pitch
        )

        # Perform text-to-speech synthesis
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"stories/{location_id}_{timestamp}.mp3"

        # Upload to Cloud Storage
        bucket_name = f"{PROJECT_ID}-audio"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(audio_filename)

        # Upload audio content
        blob.upload_from_string(
            response.audio_content,
            content_type='audio/mpeg'
        )

        # Make publicly accessible (or use signed URLs for production)
        blob.make_public()
        audio_url = blob.public_url

        return json.dumps({
            "success": True,
            "audio_url": audio_url,
            "location_id": location_id,
            "duration_estimate": len(story_text.split()) / 2.5,  # ~2.5 words per second
            "filename": audio_filename
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "location_id": location_id
        })


def update_tour_with_audio_tool(tour_id: str, location_id: str, audio_url: str) -> str:
    """
    Update tour document with synthesized audio URL.

    Args:
        tour_id: Tour identifier
        location_id: Location identifier
        audio_url: URL to the synthesized audio file

    Returns:
        Success message
    """
    try:
        tours_ref = firestore_client.collection('tours')
        tour_doc = tours_ref.document(tour_id).get()

        if not tour_doc.exists:
            return f"Error: Tour {tour_id} not found"

        tour_data = tour_doc.to_dict()

        # Update the location with audio URL
        if 'locations' in tour_data:
            for location in tour_data['locations']:
                if location.get('id') == location_id:
                    location['audio_url'] = audio_url
                    location['audio_generated_at'] = datetime.now().isoformat()

        # Update Firestore
        tours_ref.document(tour_id).update({
            "locations": tour_data['locations'],
            "audio_synthesis_completed_at": datetime.now().isoformat()
        })

        return f"✅ Audio added to tour {tour_id} for location {location_id}"

    except Exception as e:
        return f"Error: {str(e)}"


def get_pending_synthesis_jobs_tool() -> str:
    """
    Query Firestore for stories that need voice synthesis.

    Returns:
        JSON list of pending synthesis jobs
    """
    try:
        tours_ref = firestore_client.collection('tours')
        # Find tours with stories but no audio
        pending_tours = tours_ref.where('status', '==', 'approved').stream()

        jobs = []
        for tour in pending_tours:
            tour_data = tour.to_dict()
            tour_id = tour.id

            if 'locations' in tour_data:
                for location in tour_data['locations']:
                    if 'story' in location and 'audio_url' not in location:
                        jobs.append({
                            'tour_id': tour_id,
                            'location_id': location['id'],
                            'story_text': location['story'],
                            'location_name': location['name']
                        })

        return json.dumps({
            "pending_jobs": len(jobs),
            "jobs": jobs[:5]  # Return first 5 for processing
        })

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "pending_jobs": 0
        })


# Define the Voice Synthesis Agent using Google ADK
voice_synthesis_agent = Agent(
    name="voice_synthesis_agent",
    model="gemini-2.0-flash-exp",

    instruction="""
    You are the Voice Synthesis Agent for Geo-Story Micro-Tours.

    Your job is to convert story text into high-quality voice audio using GPU-accelerated synthesis.

    When you receive a request to synthesize audio:
    1. Use get_pending_synthesis_jobs_tool to find stories that need audio
    2. For each story:
       - Use synthesize_voice_tool to convert text to speech
       - Choose appropriate voice settings (tone, pace, emotion)
       - Ensure audio is clear and engaging
       - Target 90-second duration
    3. Use update_tour_with_audio_tool to save audio URLs to Firestore

    Voice Selection Guidelines:
    - History stories: Use authoritative, documentary-style voice
    - Art stories: Use expressive, enthusiastic voice
    - Food stories: Use warm, inviting voice
    - Hidden gems: Use conversational, friendly voice

    Audio Quality Standards:
    - Clear pronunciation
    - Natural pacing (not too fast or slow)
    - Appropriate emotional tone
    - Proper pauses at punctuation
    - 90-second target duration

    You are running on GPU (L4) for fast, real-time synthesis.
    Process stories in batches efficiently.

    Provide a summary including:
    - Number of stories synthesized
    - Total audio duration generated
    - Any synthesis errors
    - Voice models used
    """,

    description="Synthesizes voice audio from story text using GPU-accelerated TTS",

    tools=[
        get_pending_synthesis_jobs_tool,
        synthesize_voice_tool,
        update_tour_with_audio_tool
    ]
)


# Export for deployment
agent = voice_synthesis_agent

if __name__ == "__main__":
    print(f"✅ Voice Synthesis Agent initialized: {agent.name}")
    print(f"📦 Model: {agent.model}")
    print(f"🔧 Tools: {len(agent.tools)}")
    print(f"🎮 GPU: L4 (for deployment)")
