"""S3 MCP Server — Document upload, retrieval, and storage."""

import json
from typing import Optional

from backend.config import Config
from backend.mcp_servers.base_mcp import BaseMCP


class S3MCP(BaseMCP):

    def _build_key(self, prefix: str, case_id: str, filename: str) -> str:
        return f"{prefix}/{case_id}/{filename}"

    def upload_document(self, case_id: str, file_name: str, content_type: str, body: bytes) -> dict:
        s3_key = self._build_key("uploads", case_id, file_name)
        self.s3.put_object(
            Bucket=Config.S3_DOCUMENT_BUCKET,
            Key=s3_key,
            Body=body,
            ContentType=content_type,
        )
        return {"s3_key": s3_key, "bucket": Config.S3_DOCUMENT_BUCKET}

    def get_document(self, s3_key: str) -> Optional[bytes]:
        try:
            resp = self.s3.get_object(Bucket=Config.S3_DOCUMENT_BUCKET, Key=s3_key)
            return resp["Body"].read()
        except self.s3.exceptions.NoSuchKey:
            return None

    def list_documents(self, case_id: str) -> list[dict]:
        prefix = f"uploads/{case_id}/"
        resp = self.s3.list_objects_v2(Bucket=Config.S3_DOCUMENT_BUCKET, Prefix=prefix)
        return [
            {"key": obj["Key"], "size": obj["Size"], "last_modified": obj["LastModified"].isoformat()}
            for obj in resp.get("Contents", [])
        ]

    def store_extraction(self, case_id: str, extraction_data: dict) -> dict:
        s3_key = self._build_key("extractions", case_id, "extraction.json")
        self.s3.put_object(
            Bucket=Config.S3_DOCUMENT_BUCKET,
            Key=s3_key,
            Body=json.dumps(extraction_data).encode(),
            ContentType="application/json",
        )
        return {"s3_key": s3_key}

    def store_plan_export(self, case_id: str, plan_data: bytes, filename: str = "plan.pdf") -> dict:
        s3_key = self._build_key("exports", case_id, filename)
        self.s3.put_object(
            Bucket=Config.S3_DOCUMENT_BUCKET,
            Key=s3_key,
            Body=plan_data,
            ContentType="application/pdf",
        )
        return {"s3_key": s3_key}
