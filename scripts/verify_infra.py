"""Verify LocalStack infrastructure: DynamoDB tables, S3 buckets, read/write operations."""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3
from backend.config import Config


def get_dynamodb():
    return boto3.resource(
        "dynamodb",
        endpoint_url=Config.LOCALSTACK_ENDPOINT,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def get_s3():
    return boto3.client(
        "s3",
        endpoint_url=Config.LOCALSTACK_ENDPOINT,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def verify_tables():
    dynamodb = get_dynamodb()
    client = dynamodb.meta.client

    expected_tables = [
        Config.TABLE_CHILD_PROFILES,
        Config.TABLE_SCREENING_INPUTS,
        Config.TABLE_INTERVENTION_PLANS,
        Config.TABLE_AGENT_OUTPUTS,
        Config.TABLE_AUDIT_EVENTS,
        Config.TABLE_CLINICIAN_REVIEWS,
        Config.TABLE_CASE_COUNTER,
    ]

    existing = client.list_tables()["TableNames"]
    print(f"Found tables: {existing}")

    for table_name in expected_tables:
        if table_name not in existing:
            print(f"FAIL: Table {table_name} not found")
            return False
        print(f"  OK: {table_name}")

    return True


def verify_table_readwrite():
    dynamodb = get_dynamodb()
    table = dynamodb.Table(Config.TABLE_CHILD_PROFILES)

    table.put_item(Item={"child_id": "TEST-001", "case_id": "AIG-2026-0000", "created_at": "2026-01-01T00:00:00Z", "status": "test"})
    result = table.get_item(Key={"child_id": "TEST-001"})

    if "Item" not in result or result["Item"]["child_id"] != "TEST-001":
        print("FAIL: DynamoDB read/write test failed")
        return False

    table.delete_item(Key={"child_id": "TEST-001"})
    print("  OK: DynamoDB read/write works")
    return True


def verify_s3_bucket():
    s3 = get_s3()
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    print(f"Found buckets: {buckets}")

    if Config.S3_DOCUMENT_BUCKET not in buckets:
        print(f"FAIL: Bucket {Config.S3_DOCUMENT_BUCKET} not found")
        return False

    print(f"  OK: {Config.S3_DOCUMENT_BUCKET}")
    return True


def verify_s3_readwrite():
    s3 = get_s3()
    test_key = "test/verify.json"
    test_data = json.dumps({"test": True}).encode()

    s3.put_object(Bucket=Config.S3_DOCUMENT_BUCKET, Key=test_key, Body=test_data)
    result = s3.get_object(Bucket=Config.S3_DOCUMENT_BUCKET, Key=test_key)
    body = result["Body"].read()

    if body != test_data:
        print("FAIL: S3 read/write test failed")
        return False

    s3.delete_object(Bucket=Config.S3_DOCUMENT_BUCKET, Key=test_key)
    print("  OK: S3 read/write works")
    return True


def main():
    print("=" * 50)
    print("Infrastructure Verification")
    print("=" * 50)

    checks = [
        ("DynamoDB Tables", verify_tables),
        ("DynamoDB Read/Write", verify_table_readwrite),
        ("S3 Buckets", verify_s3_bucket),
        ("S3 Read/Write", verify_s3_readwrite),
    ]

    all_passed = True
    for name, check_fn in checks:
        print(f"\n[{name}]")
        try:
            if not check_fn():
                all_passed = False
        except Exception as e:
            print(f"FAIL: {e}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
