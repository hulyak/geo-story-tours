#!/bin/bash

# Fix all agent main.py files to use UserMessage

AGENTS_DIR="/Users/hulyakarakaya/Desktop/cloud run/geo-story-tours/agents"

for AGENT in optimizer moderator storyteller; do
  FILE="$AGENTS_DIR/$AGENT/main.py"

  echo "Fixing $AGENT..."

  # Check if file exists
  if [ -f "$FILE" ]; then
    # Add import if not present
    if ! grep -q "from google.adk.messages import UserMessage" "$FILE"; then
      sed -i '' '/^import uvicorn$/a\
from google.adk.messages import UserMessage
' "$FILE"
    fi

    # Replace the agent invocation pattern
    sed -i '' 's/async for chunk in agent\.run_async(prompt):/# Create a UserMessage as required by ADK\
        messages = [UserMessage(content=prompt)]\
\
        # Invoke the agent - it returns an async generator\
        async for event in agent.run_async(messages):/g' "$FILE"

    # Replace chunk with event in the response handling
    sed -i '' 's/async for chunk in agent\.run_async/async for event in agent.run_async/g' "$FILE"
    sed -i '' 's/if hasattr(chunk,/if hasattr(event,/g' "$FILE"
    sed-i '' 's/elif hasattr(chunk,/elif hasattr(event,/g' "$FILE"
    sed -i '' 's/full_response += str(chunk)/full_response += str(event)/g' "$FILE"

    echo "Fixed $AGENT"
  else
    echo "File not found: $FILE"
  fi
done

echo "Done!"
