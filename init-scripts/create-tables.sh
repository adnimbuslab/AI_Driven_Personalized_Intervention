#!/bin/bash
set -e

echo "Creating DynamoDB tables..."

ENDPOINT="http://localhost:4566"
PREFIX="aig_"

# ChildProfiles
awslocal dynamodb create-table \
  --table-name "${PREFIX}ChildProfiles" \
  --attribute-definitions \
    AttributeName=child_id,AttributeType=S \
    AttributeName=case_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=child_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"case_id-index","KeySchema":[{"AttributeName":"case_id","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}ChildProfiles already exists"

# ScreeningInputs
awslocal dynamodb create-table \
  --table-name "${PREFIX}ScreeningInputs" \
  --attribute-definitions \
    AttributeName=assessment_id,AttributeType=S \
    AttributeName=child_id,AttributeType=S \
    AttributeName=assessment_date,AttributeType=S \
  --key-schema AttributeName=assessment_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"child_id-index","KeySchema":[{"AttributeName":"child_id","KeyType":"HASH"},{"AttributeName":"assessment_date","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}ScreeningInputs already exists"

# InterventionPlans
awslocal dynamodb create-table \
  --table-name "${PREFIX}InterventionPlans" \
  --attribute-definitions \
    AttributeName=plan_id,AttributeType=S \
    AttributeName=child_id,AttributeType=S \
    AttributeName=case_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=plan_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"child_id-index","KeySchema":[{"AttributeName":"child_id","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"case_id-index","KeySchema":[{"AttributeName":"case_id","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}InterventionPlans already exists"

# AgentOutputs
awslocal dynamodb create-table \
  --table-name "${PREFIX}AgentOutputs" \
  --attribute-definitions \
    AttributeName=output_id,AttributeType=S \
    AttributeName=case_id,AttributeType=S \
    AttributeName=agent_id,AttributeType=S \
    AttributeName=step_number,AttributeType=N \
  --key-schema AttributeName=output_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"case_id-agent-index","KeySchema":[{"AttributeName":"case_id","KeyType":"HASH"},{"AttributeName":"agent_id","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"agent_id-index","KeySchema":[{"AttributeName":"agent_id","KeyType":"HASH"},{"AttributeName":"step_number","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}AgentOutputs already exists"

# AuditEvents
awslocal dynamodb create-table \
  --table-name "${PREFIX}AuditEvents" \
  --attribute-definitions \
    AttributeName=event_id,AttributeType=S \
    AttributeName=case_id,AttributeType=S \
    AttributeName=agent_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=event_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"case_id-time-index","KeySchema":[{"AttributeName":"case_id","KeyType":"HASH"},{"AttributeName":"timestamp","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"agent_id-time-index","KeySchema":[{"AttributeName":"agent_id","KeyType":"HASH"},{"AttributeName":"timestamp","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}AuditEvents already exists"

# ClinicianReviews
awslocal dynamodb create-table \
  --table-name "${PREFIX}ClinicianReviews" \
  --attribute-definitions \
    AttributeName=review_id,AttributeType=S \
    AttributeName=case_id,AttributeType=S \
    AttributeName=reviewer_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=review_id,KeyType=HASH \
  --global-secondary-indexes \
    '[{"IndexName":"case_id-index","KeySchema":[{"AttributeName":"case_id","KeyType":"HASH"},{"AttributeName":"timestamp","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"reviewer_id-index","KeySchema":[{"AttributeName":"reviewer_id","KeyType":"HASH"},{"AttributeName":"timestamp","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}ClinicianReviews already exists"

# CaseCounter (for atomic case ID generation)
awslocal dynamodb create-table \
  --table-name "${PREFIX}CaseCounter" \
  --attribute-definitions \
    AttributeName=counter_id,AttributeType=S \
  --key-schema AttributeName=counter_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  2>/dev/null || echo "Table ${PREFIX}CaseCounter already exists"

echo "All DynamoDB tables created successfully."
