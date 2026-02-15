"""Data models for the system design diagram agent."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ComplexityLevel(str, Enum):
    STANDARD = "standard"
    COMPLEX = "complex"
    HIGHLY_COMPLEX = "highly_complex"


class AppType(str, Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DATA_PIPELINE = "data_pipeline"
    ECOMMERCE = "ecommerce"
    SOCIAL_PLATFORM = "social_platform"
    IOT_PLATFORM = "iot_platform"
    SAAS_PLATFORM = "saas_platform"


class AuthMethod(str, Enum):
    JWT = "jwt"
    OAUTH2 = "oauth2"
    SESSION = "session"
    API_KEY = "api_key"
    NONE = "none"


class DatabaseChoice(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    DYNAMODB = "dynamodb"
    REDIS = "redis"
    MULTI = "multi"


class ScaleExpectation(str, Enum):
    SMALL = "small"          # < 1K users
    MEDIUM = "medium"        # 1K - 100K users
    LARGE = "large"          # 100K - 1M users
    MASSIVE = "massive"      # 1M+ users


class DeploymentTarget(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"


class QuestionStep(str, Enum):
    APP_NAME = "app_name"
    APP_DESCRIPTION = "app_description"
    APP_TYPE = "app_type"
    COMPLEXITY = "complexity"
    AUTH = "auth"
    DATABASE = "database"
    SCALE = "scale"
    DEPLOYMENT = "deployment"
    EXTRA_FEATURES = "extra_features"
    COMPLETE = "complete"


# Define the conversation flow — which question follows which
QUESTION_FLOW = [
    QuestionStep.APP_NAME,
    QuestionStep.APP_DESCRIPTION,
    QuestionStep.APP_TYPE,
    QuestionStep.COMPLEXITY,
    QuestionStep.AUTH,
    QuestionStep.DATABASE,
    QuestionStep.SCALE,
    QuestionStep.DEPLOYMENT,
    QuestionStep.EXTRA_FEATURES,
    QuestionStep.COMPLETE,
]


class SessionState(BaseModel):
    """Tracks the state of one user's design session."""

    session_id: str
    current_step: QuestionStep = QuestionStep.APP_NAME
    app_name: Optional[str] = None
    app_description: Optional[str] = None
    app_type: Optional[AppType] = None
    complexity: Optional[ComplexityLevel] = None
    auth_method: Optional[AuthMethod] = None
    database: Optional[DatabaseChoice] = None
    scale: Optional[ScaleExpectation] = None
    deployment: Optional[DeploymentTarget] = None
    extra_features: list[str] = []
    diagram_mermaid: Optional[str] = None


class AgentMessage(BaseModel):
    """A message from the agent to the user."""

    text: str
    options: list[str] | None = None
    is_free_text: bool = False
    diagram: str | None = None
    is_complete: bool = False


class UserResponse(BaseModel):
    """A response from the user."""

    session_id: str
    answer: str
