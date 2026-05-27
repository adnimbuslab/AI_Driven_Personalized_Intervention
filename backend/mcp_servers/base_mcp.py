import boto3
from backend.config import Config


class BaseMCP:
    def __init__(self):
        self._dynamodb_resource = None
        self._dynamodb_client = None
        self._s3_client = None

    @property
    def dynamodb(self):
        if self._dynamodb_resource is None:
            self._dynamodb_resource = boto3.resource(
                "dynamodb",
                endpoint_url=Config.LOCALSTACK_ENDPOINT,
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            )
        return self._dynamodb_resource

    @property
    def dynamodb_client(self):
        if self._dynamodb_client is None:
            self._dynamodb_client = boto3.client(
                "dynamodb",
                endpoint_url=Config.LOCALSTACK_ENDPOINT,
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            )
        return self._dynamodb_client

    @property
    def s3(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=Config.LOCALSTACK_ENDPOINT,
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            )
        return self._s3_client

    def _get_table(self, table_name: str):
        return self.dynamodb.Table(table_name)
