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
pip install -r requirements.txt
```
### 2. Create ENV file

Create ```.env``` file in the root folder and add openai api key as ```OPENAI_API_KEY = "sk-proj********"```

### 3. Run the FAST API (Backend) Server
```bash
python app.py
```
Server starts at: ```http://localhost:8000```

### 4. Run Streamlit (in a new terminal)
```bash
streamlit run streamlit_app.py
```
Open your browser at ```http://localhost:8501``` and have fun.


















