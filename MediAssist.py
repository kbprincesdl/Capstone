from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import TypedDict

from langgraph.graph import StateGraph

# ---------------------------
# ✅ DEFINE STATE (IMPORTANT)
# ---------------------------
class AgentState(TypedDict):
    input: str
    intent: str
    response: str

# ---------------------------
# ✅ NODES
# ---------------------------

# Step 1: Identify intent
def triage_node(state: AgentState):
    user_input = state["input"].lower()

    if "bill" in user_input:
        intent = "billing"
    elif "doctor" in user_input:
        intent = "medical"
    else:
        intent = "general"

    return {"intent": intent}


# Step 2: Generate response
def response_node(state: AgentState):
    intent = state["intent"]

    if intent == "billing":
        reply = "This is a billing issue. Redirecting to billing support."
    elif intent == "medical":
        reply = "This is a medical query. Connecting to doctor support."
    else:
        reply = "This is a general inquiry. How can I assist you?"

    return {"response": reply}


# ---------------------------
# ✅ BUILD GRAPH
# ---------------------------
builder = StateGraph(AgentState)

builder.add_node("triage", triage_node)
builder.add_node("response", response_node)

builder.set_entry_point("triage")
builder.add_edge("triage", "response")

graph = builder.compile()

# ---------------------------
# ✅ FASTAPI APP
# ---------------------------
app = FastAPI()

# ✅ FIX CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# ✅ API ENDPOINT
# ---------------------------
@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/triage")
async def triage_api(data: dict):
    user_input = data.get("message", "")

    result = graph.invoke({
        "input": user_input
    })

    return {
        "intent": result.get("intent"),
        "response": result.get("response")
    }
