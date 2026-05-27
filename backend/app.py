"""FastAPI application wrapping all Lambda handlers.

Run with: uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import json
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import Config

app = FastAPI(
    title="AI-Driven Personalized Intervention Guideline Generator",
    description="Governance-Aware Agentic AI for autism intervention planning",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _call_handler(handler_fn, event):
    result = handler_fn(event, None)
    status = result.get("statusCode", 200)
    body = result.get("body", "{}")
    if isinstance(body, str):
        body = json.loads(body)
    return JSONResponse(content=body, status_code=status)


# --- Case Management ---

@app.post("/api/cases", status_code=201)
async def create_case(request: Request):
    from backend.lambdas.case_intake_handler import handler
    body = await request.json()
    return _call_handler(handler, {"body": json.dumps(body)})


@app.get("/api/cases")
async def list_cases():
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": "/api/cases", "pathParameters": {}})


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/status")
async def get_case_status(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/status", "pathParameters": {"case_id": case_id}})


@app.put("/api/cases/{case_id}/consent")
async def update_consent(case_id: str, request: Request):
    from backend.mcp_servers.audit_mcp import AuditMCP
    body = await request.json()
    audit = AuditMCP()
    audit.log_event(
        case_id=case_id,
        agent_id="system",
        event_type="CONSENT_CHECK",
        action=f"Consent updated: {body.get('granted', False)}",
    )
    return JSONResponse(content={"case_id": case_id, "consent_status": "GRANTED" if body.get("granted") else "DENIED"})


# --- Documents ---

@app.post("/api/cases/{case_id}/documents")
async def upload_document(case_id: str, request: Request):
    from backend.lambdas.document_upload_handler import handler
    body = await request.json()
    return _call_handler(handler, {
        "pathParameters": {"case_id": case_id},
        "body": json.dumps(body),
    })


@app.post("/api/cases/{case_id}/inputs")
async def submit_inputs(case_id: str, request: Request):
    from backend.mcp_servers.dynamo_mcp import DynamoMCP
    body = await request.json()
    dynamo = DynamoMCP()
    dynamo.put_screening_input(assessment_id=f"ASS-{case_id}", data={"child_id": body.get("child_id", ""), **body})
    return JSONResponse(content={"case_id": case_id, "status": "inputs_saved"})


@app.post("/api/cases/{case_id}/followup")
async def submit_followup(case_id: str, request: Request):
    body = await request.json()
    return JSONResponse(content={"case_id": case_id, "round": body.get("round", 1), "status": "received"})


@app.get("/api/cases/{case_id}/inputs")
async def get_inputs(case_id: str):
    from backend.mcp_servers.dynamo_mcp import DynamoMCP
    dynamo = DynamoMCP()
    child_id = case_id.replace("AIG-", "CH-").rsplit("-", 1)[-1] if "AIG-" in case_id else case_id
    inputs = dynamo.get_screening_inputs(child_id)
    return JSONResponse(content={"case_id": case_id, "inputs": inputs})


# --- Workflow ---

@app.post("/api/cases/{case_id}/workflow/start")
async def start_workflow(case_id: str, request: Request):
    from backend.lambdas.workflow_orchestrator import handler
    body = await request.json()
    return _call_handler(handler, {
        "pathParameters": {"case_id": case_id},
        "body": json.dumps(body),
    })


@app.get("/api/cases/{case_id}/workflow/state")
async def get_workflow_state(case_id: str):
    from backend.mcp_servers.workflow_mcp import WorkflowMCP
    wf = WorkflowMCP()
    state = wf.get_workflow_state(case_id)
    return JSONResponse(content=state or {"case_id": case_id, "status": "not_found"})


@app.post("/api/cases/{case_id}/escalate")
async def escalate_case(case_id: str, request: Request):
    from backend.mcp_servers.workflow_mcp import WorkflowMCP
    body = await request.json()
    wf = WorkflowMCP()
    result = wf.trigger_escalation(case_id, "manual", body.get("reason", "Manual escalation"))
    return JSONResponse(content=result)


# --- Plan ---

@app.get("/api/cases/{case_id}/plan")
async def get_plan(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/plan/profile")
async def get_plan_profile(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan/profile", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/plan/domains")
async def get_plan_domains(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan/domains", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/plan/guidelines")
async def get_plan_guidelines(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan/guidelines", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/plan/goals")
async def get_plan_goals(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan/goals", "pathParameters": {"case_id": case_id}})


@app.get("/api/cases/{case_id}/plan/caregiver")
async def get_plan_caregiver(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/plan/caregiver", "pathParameters": {"case_id": case_id}})


# --- Review ---

@app.get("/api/reviews/pending")
async def get_pending_reviews(reviewer_id: str = ""):
    from backend.lambdas.review_queue_handler import handler
    return _call_handler(handler, {"queryStringParameters": {"reviewer_id": reviewer_id}})


@app.post("/api/cases/{case_id}/review")
async def submit_review(case_id: str, request: Request):
    from backend.lambdas.clinician_review_handler import handler
    body = await request.json()
    return _call_handler(handler, {
        "pathParameters": {"case_id": case_id},
        "body": json.dumps(body),
    })


@app.get("/api/cases/{case_id}/reviews")
async def get_reviews(case_id: str):
    from backend.mcp_servers.dynamo_mcp import DynamoMCP
    dynamo = DynamoMCP()
    reviews = dynamo.query_by_case(case_id, Config.TABLE_CLINICIAN_REVIEWS)
    return JSONResponse(content={"case_id": case_id, "reviews": reviews})


# --- Audit ---

@app.get("/api/cases/{case_id}/audit")
async def get_audit_trail(case_id: str):
    from backend.lambdas.case_query_handler import handler
    return _call_handler(handler, {"path": f"/api/cases/{case_id}/audit", "pathParameters": {"case_id": case_id}})


@app.get("/api/audit/agent/{agent_id}")
async def get_agent_audit(agent_id: str, from_date: str = "", to_date: str = ""):
    from backend.mcp_servers.audit_mcp import AuditMCP
    audit = AuditMCP()
    events = audit.get_agent_audit_trail(agent_id, from_date or None, to_date or None)
    return JSONResponse(content={"agent_id": agent_id, "events": events})


# --- Chat ---

@app.post("/api/chat/{case_id}/message")
async def send_chat_message(case_id: str, request: Request):
    from backend.lambdas.chat_handler import handler
    body = await request.json()
    return _call_handler(handler, {
        "pathParameters": {"case_id": case_id},
        "httpMethod": "POST",
        "body": json.dumps(body),
    })


@app.get("/api/chat/{case_id}/history")
async def get_chat_history(case_id: str):
    from backend.lambdas.chat_handler import handler
    return _call_handler(handler, {
        "pathParameters": {"case_id": case_id},
        "httpMethod": "GET",
    })


# --- Health ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "aig-api"}
