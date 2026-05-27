"""Atomic case ID generation using DynamoDB counter."""

from datetime import datetime, timezone

import boto3
from backend.config import Config


def generate_case_id() -> str:
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=Config.LOCALSTACK_ENDPOINT,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )
    table = dynamodb.Table(Config.TABLE_CASE_COUNTER)
    year = datetime.now(timezone.utc).strftime("%Y")
    counter_id = f"case_counter_{year}"

    resp = table.update_item(
        Key={"counter_id": counter_id},
        UpdateExpression="SET counter_value = if_not_exists(counter_value, :start) + :inc",
        ExpressionAttributeValues={":start": 0, ":inc": 1},
        ReturnValues="UPDATED_NEW",
    )
    seq = int(resp["Attributes"]["counter_value"])
    return f"{Config.CASE_ID_PREFIX}-{year}-{seq:04d}"
