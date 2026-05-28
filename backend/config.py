import os


class Config:
    LLM_MODEL_ID = os.environ.get("LLM_MODEL_ID", "claude-opus-4-7")
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

    CONFIDENCE_THRESHOLD_DEFAULT = float(os.environ.get("CONFIDENCE_THRESHOLD_DEFAULT", "0.70"))
    CONFIDENCE_THRESHOLD_PREDICTION = float(os.environ.get("CONFIDENCE_THRESHOLD_PREDICTION", "0.75"))
    CONFIDENCE_THRESHOLD_GUIDELINE = float(os.environ.get("CONFIDENCE_THRESHOLD_GUIDELINE", "0.70"))
    DATA_COMPLETENESS_THRESHOLD = float(os.environ.get("DATA_COMPLETENESS_THRESHOLD", "0.60"))
    MAX_FOLLOWUP_ROUNDS = int(os.environ.get("MAX_FOLLOWUP_ROUNDS", "3"))
    BIAS_SENSITIVITY = os.environ.get("BIAS_SENSITIVITY", "medium")

    LOCALSTACK_ENDPOINT = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    DYNAMODB_TABLE_PREFIX = os.environ.get("DYNAMODB_TABLE_PREFIX", "aig_")
    S3_DOCUMENT_BUCKET = os.environ.get("S3_DOCUMENT_BUCKET", "aig-documents")

    CASE_ID_PREFIX = os.environ.get("CASE_ID_PREFIX", "AIG")
    AUDIT_RETENTION_DAYS = int(os.environ.get("AUDIT_RETENTION_DAYS", "2555"))

    API_HOST = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT = int(os.environ.get("API_PORT", "8000"))
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")

    # Table names
    TABLE_CHILD_PROFILES = f"{DYNAMODB_TABLE_PREFIX}ChildProfiles"
    TABLE_SCREENING_INPUTS = f"{DYNAMODB_TABLE_PREFIX}ScreeningInputs"
    TABLE_INTERVENTION_PLANS = f"{DYNAMODB_TABLE_PREFIX}InterventionPlans"
    TABLE_AGENT_OUTPUTS = f"{DYNAMODB_TABLE_PREFIX}AgentOutputs"
    TABLE_AUDIT_EVENTS = f"{DYNAMODB_TABLE_PREFIX}AuditEvents"
    TABLE_CLINICIAN_REVIEWS = f"{DYNAMODB_TABLE_PREFIX}ClinicianReviews"
    TABLE_CASE_COUNTER = f"{DYNAMODB_TABLE_PREFIX}CaseCounter"

    @classmethod
    def get_confidence_threshold(cls, agent_id: str) -> float:
        thresholds = {
            "prediction": cls.CONFIDENCE_THRESHOLD_PREDICTION,
            "guideline-generation": cls.CONFIDENCE_THRESHOLD_GUIDELINE,
        }
        return thresholds.get(agent_id, cls.CONFIDENCE_THRESHOLD_DEFAULT)
