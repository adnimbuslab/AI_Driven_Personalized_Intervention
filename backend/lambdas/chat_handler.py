"""Chat handler — Processes conversational messages during intake."""

import json
import uuid
from datetime import datetime, timezone
from backend.mcp_servers.llm_mcp import LlmMCP


_chat_histories = {}


def handler(event, context):
    case_id = event.get("pathParameters", {}).get("case_id", "")
    method = event.get("httpMethod", "POST")

    if method == "GET":
        history = _chat_histories.get(case_id, [])
        return _response(200, {"case_id": case_id, "messages": history})

    body = event.get("body", {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return _response(400, {"error": "Invalid request body"})

    message = body.get("message", "")
    if not message:
        return _response(400, {"error": "message is required"})

    if case_id not in _chat_histories:
        _chat_histories[case_id] = []

    _chat_histories[case_id].append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    llm = LlmMCP()
    response = llm.generate(
        system_prompt=(
            "You are a clinical intake assistant collecting autism screening information. "
            "Ask clear, focused questions to gather the information needed for intervention planning. "
            "Be warm and professional. Do not diagnose. "
            "If the reporter provides screening data, acknowledge it and ask follow-up questions about missing fields."
        ),
        user_prompt=f"Reporter message: {message}\n\nChat history: {json.dumps(_chat_histories[case_id][-5:])}",
    )

    assistant_msg = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": response.get("content", "Thank you for the information. Could you provide more details?"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _chat_histories[case_id].append(assistant_msg)

    return _response(200, {
        "response": assistant_msg,
        "case_id": case_id,
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
