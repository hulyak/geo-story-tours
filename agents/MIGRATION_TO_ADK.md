# Migration to Google ADK - Critical for Hackathon

## ⚠️ Current Status

**Problem**: Our agents use Flask, NOT the official Google Agent Development Kit (ADK).

**Hackathon Requirement**:
> "Your agent must be built with Google's Agent Development Kit (ADK)"

**Impact**: Without proper ADK, we won't qualify for the AI Agents category! ❌

---

## ✅ Solution: Use Official Google ADK

### What is ADK?

Google's Agent Development Kit is a specific framework (not just any Python agent framework):

```python
from google.adk.agents import LlmAgent

# This is what judges expect to see!
agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a helpful assistant...",
    tools=[tool1, tool2]
)
```

### Installation

```bash
pip install google-adk
```

---

## 🔄 Quick Migration Path

### Option 1: Full ADK Refactor (Recommended for Hackathon)

**Time**: 4-6 hours
**Compliance**: 100% ✅
**Demo Impact**: Excellent

Convert all 4 agents to proper ADK agents:

```python
# agents/storyteller/adk_agent.py
from google.adk.agents import LlmAgent

storytelling_agent = LlmAgent(
    name="storytelling_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a master storyteller...",
    tools=[generate_story_tool, save_to_firestore_tool]
)
```

**Deploy with**:
```bash
cd agents/storyteller
adk deploy cloud_run
```

### Option 2: Hybrid ADK Wrapper (Fastest)

**Time**: 1-2 hours
**Compliance**: 80% ✅
**Demo Impact**: Good

Keep our Flask logic but wrap it in ADK:

```python
from google.adk.agents import LlmAgent
from flask import Flask

# ADK agent that delegates to Flask
agent = LlmAgent(name="agent", ...)

# Flask app for HTTP endpoints
app = Flask(__name__)

@app.route('/process')
def process():
    result = agent.run(request.json)
    return jsonify(result)
```

### Option 3: Multi-Agent Coordinator (Best Demo)

**Time**: 6-8 hours
**Compliance**: 100% ✅✅
**Demo Impact**: AMAZING 🤩

Create one coordinator agent that manages all 4 sub-agents:

```python
from google.adk.agents import LlmAgent

# Define sub-agents
curator = LlmAgent(name="curator", model="gemini-2.0-flash-exp", ...)
optimizer = LlmAgent(name="optimizer", model="gemini-2.0-flash-exp", ...)
storyteller = LlmAgent(name="storyteller", model="gemini-2.0-flash-exp", ...)
moderator = LlmAgent(name="moderator", model="gemini-2.0-flash-exp", ...)

# Coordinator with sub-agents
tour_coordinator = LlmAgent(
    name="tour_coordinator",
    model="gemini-2.0-flash-exp",
    description="Orchestrates 4 specialized agents to create personalized tours",
    sub_agents=[curator, optimizer, storyteller, moderator]
)
```

---

## 📝 Step-by-Step: Option 1 (Recommended)

### 1. Restructure Project

```
agents/
├── coordinator/              # NEW: Main coordinator agent
│   ├── agent.py             # ADK coordinator
│   └── requirements.txt
│
├── curator/
│   ├── agent.py             # Refactored to ADK
│   └── requirements.txt
│
├── optimizer/
│   ├── agent.py             # Refactored to ADK
│   └── requirements.txt
│
├── storyteller/
│   ├── adk_agent.py         # ✅ Already started!
│   └── requirements.txt
│
└── moderator/
    ├── agent.py             # Refactored to ADK
    └── requirements.txt
```

### 2. Refactor Each Agent

**Template**:
```python
from google.adk.agents import LlmAgent

def my_tool_function(arg1, arg2):
    """Tool description"""
    # Your existing logic here
    return result

agent = LlmAgent(
    name="agent_name",
    model="gemini-2.0-flash-exp",
    instruction="""
    Detailed instructions for what this agent does.

    When to use tools:
    - Use my_tool_function when...
    """,
    description="Brief description",
    tools=[my_tool_function]
)
```

### 3. Deploy with ADK

```bash
cd agents/storyteller
adk deploy cloud_run \
  --project=durable-torus-477513-g3 \
  --region=europe-west1
```

This automatically:
- ✅ Builds container
- ✅ Deploys to Cloud Run
- ✅ Sets up endpoints
- ✅ Configures secrets

---

## 🎯 What Judges Want to See

### In the Demo Video:

1. **Show ADK import**:
   ```python
   from google.adk.agents import LlmAgent  # ← Point this out!
   ```

2. **Show agent definition**:
   ```python
   storytelling_agent = LlmAgent(
       name="storytelling_agent",
       model="gemini-2.0-flash-exp",  # ← Using Gemini!
       tools=[...]  # ← Agent has tools!
   )
   ```

3. **Show deployment**:
   ```bash
   adk deploy cloud_run  # ← One command deployment!
   ```

4. **Show agents collaborating**:
   - Cloud Console: Show all 4 Cloud Run services
   - Logs: Show agent-to-agent communication
   - Pub/Sub: Show messages flowing

### In the Architecture Diagram:

```
User Request
    ↓
[Coordinator Agent (ADK)] ← Label as "Google ADK"
    ↓
┌─────────────┬─────────────┬─────────────┐
│   Curator   │  Optimizer  │ Storyteller │
│  (ADK Sub)  │  (ADK Sub)  │  (ADK Sub)  │
└─────────────┴─────────────┴─────────────┘
                    ↓
            [Moderator (ADK)]
```

---

## 🚀 Migration Checklist

- [ ] Install ADK: `pip install google-adk`
- [ ] Convert Storytelling Agent (already started in `adk_agent.py`)
- [ ] Convert Curator Agent
- [ ] Convert Optimizer Agent
- [ ] Convert Moderator Agent
- [ ] Create Coordinator Agent (optional but impressive)
- [ ] Test locally: `python agent.py`
- [ ] Deploy: `adk deploy cloud_run`
- [ ] Update README to show ADK usage
- [ ] Update demo script to highlight ADK
- [ ] Update architecture diagram with "ADK" labels

---

## 💡 Quick Win: Start with Storyteller

I've already created `adk_agent.py` for the Storytelling Agent! This is your proof of concept.

**Test it**:
```bash
cd agents/storyteller
pip install -r requirements.txt
python adk_agent.py
```

**Deploy it**:
```bash
adk deploy cloud_run --project=durable-torus-477513-g3
```

Once this works, replicate for the other 3 agents.

---

## ⏰ Time Estimate

**Full ADK Migration**: 6-8 hours
- Storyteller: ✅ Done (1 hour)
- Curator: 2 hours
- Optimizer: 1.5 hours
- Moderator: 1.5 hours
- Coordinator: 2 hours
- Testing & deployment: 1 hour

**Benefit**: 100% compliant, impressive demo, likely to win 🏆

---

## 🎬 Updated Demo Script

**0:00-0:30**: "This app uses Google's Agent Development Kit..."

**Show code**:
```python
from google.adk.agents import LlmAgent

storytelling_agent = LlmAgent(
    name="storytelling_agent",
    model="gemini-2.0-flash-exp",
    tools=[...]
)
```

**0:30-1:00**: "4 ADK agents collaborate..."

**Show Cloud Run services**: All deployed with `adk deploy cloud_run`

**1:00-2:00**: "Watch the agents work..."

**Show real-time**: Logs showing agent calls, Gemini generating stories

**2:00-3:00**: "All powered by ADK on Cloud Run"

---

## 🏆 Why This Wins

1. **Compliance**: Uses actual ADK framework ✅
2. **Innovation**: 4 specialized agents + coordinator
3. **Technical**: Sophisticated tool usage, proper architecture
4. **Demo**: Visual proof of multi-agent collaboration
5. **Google Tech**: ADK + Gemini + Cloud Run + Pub/Sub

---

## 📚 Resources

- [ADK GitHub](https://github.com/google/adk-python)
- [ADK Docs](https://google.github.io/adk-docs/)
- [Cloud Run Deployment](https://google.github.io/adk-docs/deploy/cloud-run/)
- [Multi-Agent Systems](https://google.github.io/adk-docs/guides/multi-agent/)

---

**Next Step**: Focus on migrating to ADK. Once that's done, the other tasks (mock data, tour pages, demo video) will be much easier and more impressive!

Want me to help convert the Curator Agent next?
