from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from devai.intent.parser import IntentParser
from devai.planner.deployment_planner import AIPlanner
from devai.planner.validation import SchemaValidator
from devai.execution.engine import ExecutionEngine
from devai.plugins.registry import PluginRegistry
from devai.core.exceptions import DevAIException
from devai.policy.policy_engine import PolicyEngine
from fastapi.responses import FileResponse
import os

app = FastAPI(title="DevAI API")
registry = PluginRegistry()
registry.load_plugins()


@app.get("/")
async def get_index():
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "static", "index.html"))


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    status: str
    message: str
    plan: Optional[dict] = None


class ExecuteRequest(BaseModel):
    plan: dict
    approved: bool = False


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        parser = IntentParser()
        parser.parse(request.message)

        planner = AIPlanner()
        raw_plan = planner.generate_plan(request.message)

        validator = SchemaValidator()
        validated_plan = validator.validate_plan(raw_plan)
        validator.enforce_security_policies(validated_plan)
        policy = PolicyEngine().evaluate(validated_plan, validated_plan.metadata.environment)
        preview = ExecutionEngine(registry=registry).preview(validated_plan)

        return ChatResponse(
            status="planned",
            message="Plan generated and validated. Review the dry-run preview, then explicitly approve execution.",
            plan={
                "plan": validated_plan.model_dump(),
                "policy": policy.model_dump(),
                "preview": preview.model_dump(),
            },
        )

    except DevAIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/dry-run", response_model=ChatResponse)
async def dry_run_endpoint(request: ExecuteRequest):
    try:
        validator = SchemaValidator()
        validated_plan = validator.validate_plan(request.plan)
        validator.enforce_security_policies(validated_plan)
        preview = ExecutionEngine(registry=registry).preview(validated_plan)
        return ChatResponse(
            status="dry-run",
            message="Dry run completed. No changes were executed.",
            plan=preview.model_dump(),
        )
    except DevAIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dry run error: {str(e)}")


@app.post("/execute", response_model=ChatResponse)
async def execute_endpoint(request: ExecuteRequest):
    try:
        validator = SchemaValidator()
        validated_plan = validator.validate_plan(request.plan)

        if not request.approved:
            raise HTTPException(status_code=400, detail="Execution requires explicit approval.")

        engine = ExecutionEngine(registry=registry)
        report = engine.execute(validated_plan, approval_callback=lambda _: request.approved)

        return ChatResponse(
            status="executed",
            message="Infrastructure deployed successfully!",
            plan=report.model_dump(),
        )
    except HTTPException:
        raise
    except DevAIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
