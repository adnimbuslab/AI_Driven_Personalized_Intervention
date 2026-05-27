"""Document upload handler — Uploads screening documents to S3."""

import json
import uuid
from backend.mcp_servers.s3_mcp import S3MCP
from backend.mcp_servers.audit_mcp import AuditMCP


def handler(event, context):
    case_id = event.get("pathParameters", {}).get("case_id", "")
    if not case_id:
        return _response(400, {"error": "case_id is required"})

    body = event.get("body", {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return _response(400, {"error": "Invalid request body"})

    file_name = body.get("file_name", f"document-{uuid.uuid4().hex[:8]}.pdf")
    content_type = body.get("content_type", "application/pdf")
    content = body.get("content", "").encode() if isinstance(body.get("content"), str) else b""

    s3 = S3MCP()
    result = s3.upload_document(
        case_id=case_id,
        file_name=file_name,
        content_type=content_type,
        body=content,
    )

    audit = AuditMCP()
    audit.log_event(
        case_id=case_id,
        agent_id="system",
        event_type="DOCUMENT_UPLOAD",
        action=f"Document uploaded: {file_name}",
        metadata={"s3_key": result["s3_key"], "content_type": content_type},
    )

    return _response(200, {
        "document_id": f"DOC-{uuid.uuid4().hex[:8]}",
        "s3_key": result["s3_key"],
        "file_name": file_name,
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
