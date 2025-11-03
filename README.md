# Intent-Routed Agent (POC)

A **natural language agent** that:
- Classifies user intent
- Routes to the right tools
- Executes a multi-node workflow
- Maintains conversation state
- Returns **answer + execution trace**

Built with **LangGraph**, **LangChain**, **FastAPI**, and **session-based memory**.

---

## Features

| Feature | Status |
|-------|--------|
| Intent classification | Yes |
| Tool routing (HTTP, Time, etc.) | Yes |
| Multi-step graph (`initial_analysis → react_agent → tools → final_analysis`) | Yes |
| Session-based memory (follow-up questions) | Yes |
| FastAPI wrapper with `/chat` endpoint | Yes |
| Execution trace included in response | Yes |
| Swagger UI (`/docs`) | Yes |

---

## Architecture
User Query
↓
[initial_analysis] → (irrelevant?) → END
↓
[react_agent] → (needs tool?) → [tools] → back to react_agent
↓
[final_analysis] → (needs clarification?) → loop or summarize
↓
[summarize_conversation] → Final Answer + Trace
text- **State**: `State` (from `AIAgent`)
- **Memory**: `MemorySaver` + `thread_id` (per session)
- **Tools**: HTTP REST, current time, (extendable)

---

## Quick Start

### 1. Install dependencies

```bash
pip install fastapi uvicorn langgraph langchain-openai requests pydantic
```

### 2. Run the API
```bash
python app.py
```
Server starts at: ```http://localhost:8000```
### 3. Try it
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current date and time?"}'
```




















MethodEndpointDescriptionPOST/chatSend message, get answer + traceGET/Health checkDELETE/session/{id}Clear session (optional)
Swagger UI: http://localhost:8000/docs

Project Structure
textsrc/
├── agent/
│   ├── ai_agent.py         ← AIAgent with node logic
│   ├── tools.py            ← ToolDefinitions (HTTP, time, etc.)
│   └── graph_builder.py    ← BotPipeline + graph definition
├── app.py                  ← FastAPI wrapper
└── README.md