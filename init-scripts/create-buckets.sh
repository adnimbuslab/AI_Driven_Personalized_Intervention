#!/bin/bash
set -e

echo "Creating S3 buckets..."

awslocal s3 mb s3://aig-documents 2>/dev/null || echo "Bucket aig-documents already exists"

echo "All S3 buckets created successfully."
