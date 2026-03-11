from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from devai.intent.parser import IntentParser
from devai.ai.planner import AIPlanner
from devai.validation.validator import SchemaValidator
from devai.execution.engine import ExecutionEngine
from devai.plugins.registry import PluginRegistry
from devai.core.exceptions import DevAIException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os

app = FastAPI(title="DevAI API")
registry = PluginRegistry()
registry.load_plugins()

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    message: str
    plan: Optional[dict] = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Parse Intent
        parser = IntentParser()
        intent = parser.parse(request.message)
        
        # 2. AI Planning
        planner = AIPlanner()
        raw_plan = planner.generate_plan(request.message)
        
        # 3. Validation
        validator = SchemaValidator()
        validated_plan = validator.validate_plan(raw_plan)
        validator.enforce_security_policies(validated_plan)
        
        return ChatResponse(
            status="planned",
            message="Plan generated and validated. Please approve to execute.",
            plan=validated_plan.model_dump()
        )
        
    except DevAIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/execute", response_model=ChatResponse)
async def execute_endpoint(plan: dict):
    try:
        validator = SchemaValidator()
        validated_plan = validator.validate_plan(plan)
        
        engine = ExecutionEngine(registry=registry)
        engine.execute(validated_plan)
        
        return ChatResponse(
            status="executed",
            message="Infrastructure deployed successfully!"
        )
    except DevAIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
