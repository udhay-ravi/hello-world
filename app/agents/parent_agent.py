"""Parent Agent — orchestrates the conversation flow with the user.

Responsibilities:
- Present questions with options to the user
- Validate and store answers
- Advance through the question flow
- Hand off to the Worker Agent when all info is collected
"""

from __future__ import annotations

from app.models import (
    AgentMessage,
    AppType,
    AuthMethod,
    ComplexityLevel,
    DatabaseChoice,
    DeploymentTarget,
    QuestionStep,
    ScaleExpectation,
    SessionState,
    QUESTION_FLOW,
)


def _next_step(current: QuestionStep) -> QuestionStep:
    idx = QUESTION_FLOW.index(current)
    if idx + 1 < len(QUESTION_FLOW):
        return QUESTION_FLOW[idx + 1]
    return QuestionStep.COMPLETE


# ── Question generators ──────────────────────────────────────────────

def _ask_app_name() -> AgentMessage:
    return AgentMessage(
        text=(
            "Welcome! I'm your System Design Architect agent.\n\n"
            "I'll guide you through a series of questions to understand your "
            "application, then generate a full system design architecture diagram.\n\n"
            "**Let's start — what is the name of your application?**"
        ),
        is_free_text=True,
    )


def _ask_app_description() -> AgentMessage:
    return AgentMessage(
        text="Great! Now give me a **brief description** of what the app does (1-3 sentences).",
        is_free_text=True,
    )


def _ask_app_type() -> AgentMessage:
    return AgentMessage(
        text="What **type of application** are you building?",
        options=[
            "Web Application",
            "Mobile Application",
            "API / Microservice",
            "Data Pipeline",
            "E-Commerce Platform",
            "Social Platform",
            "IoT Platform",
            "SaaS Platform",
        ],
    )


def _ask_complexity() -> AgentMessage:
    return AgentMessage(
        text=(
            "What **complexity level** do you want for the architecture?\n\n"
            "- **Standard** — Clean monolith or simple client-server. Good for MVPs and small teams.\n"
            "- **Complex** — Microservices, caching layers, message queues, CI/CD.\n"
            "- **Highly Complex** — Distributed systems, multi-region, event-driven, CQRS/ES, service mesh."
        ),
        options=["Standard", "Complex", "Highly Complex"],
    )


def _ask_auth() -> AgentMessage:
    return AgentMessage(
        text="What **authentication method** should the system use?",
        options=["JWT Tokens", "OAuth 2.0 / SSO", "Session-based", "API Key", "None"],
    )


def _ask_database() -> AgentMessage:
    return AgentMessage(
        text="What is your preferred **database**?",
        options=[
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "DynamoDB",
            "Redis (cache-first)",
            "Multi-database (polyglot persistence)",
        ],
    )


def _ask_scale() -> AgentMessage:
    return AgentMessage(
        text="What **scale** do you expect?",
        options=[
            "Small (< 1K users)",
            "Medium (1K – 100K users)",
            "Large (100K – 1M users)",
            "Massive (1M+ users)",
        ],
    )


def _ask_deployment() -> AgentMessage:
    return AgentMessage(
        text="Where will the application be **deployed**?",
        options=["AWS", "Google Cloud (GCP)", "Azure", "On-Premise", "Hybrid"],
    )


def _ask_extra_features() -> AgentMessage:
    return AgentMessage(
        text=(
            "Select any **additional features** you need (comma-separated numbers, or type 'none'):\n\n"
            "1. Real-time / WebSockets\n"
            "2. Full-text Search\n"
            "3. File / Media Storage\n"
            "4. Notifications (push/email)\n"
            "5. Analytics / Monitoring\n"
            "6. Rate Limiting\n"
            "7. Background Jobs / Task Queue\n"
            "8. CDN for static assets"
        ),
        is_free_text=True,
    )


QUESTION_MAP = {
    QuestionStep.APP_NAME: _ask_app_name,
    QuestionStep.APP_DESCRIPTION: _ask_app_description,
    QuestionStep.APP_TYPE: _ask_app_type,
    QuestionStep.COMPLEXITY: _ask_complexity,
    QuestionStep.AUTH: _ask_auth,
    QuestionStep.DATABASE: _ask_database,
    QuestionStep.SCALE: _ask_scale,
    QuestionStep.DEPLOYMENT: _ask_deployment,
    QuestionStep.EXTRA_FEATURES: _ask_extra_features,
}


# ── Answer processors ────────────────────────────────────────────────

_APP_TYPE_MAP = {
    "web application": AppType.WEB_APP,
    "mobile application": AppType.MOBILE_APP,
    "api / microservice": AppType.API_SERVICE,
    "data pipeline": AppType.DATA_PIPELINE,
    "e-commerce platform": AppType.ECOMMERCE,
    "social platform": AppType.SOCIAL_PLATFORM,
    "iot platform": AppType.IOT_PLATFORM,
    "saas platform": AppType.SAAS_PLATFORM,
}

_COMPLEXITY_MAP = {
    "standard": ComplexityLevel.STANDARD,
    "complex": ComplexityLevel.COMPLEX,
    "highly complex": ComplexityLevel.HIGHLY_COMPLEX,
}

_AUTH_MAP = {
    "jwt tokens": AuthMethod.JWT,
    "oauth 2.0 / sso": AuthMethod.OAUTH2,
    "session-based": AuthMethod.SESSION,
    "api key": AuthMethod.API_KEY,
    "none": AuthMethod.NONE,
}

_DB_MAP = {
    "postgresql": DatabaseChoice.POSTGRESQL,
    "mysql": DatabaseChoice.MYSQL,
    "mongodb": DatabaseChoice.MONGODB,
    "dynamodb": DatabaseChoice.DYNAMODB,
    "redis (cache-first)": DatabaseChoice.REDIS,
    "multi-database (polyglot persistence)": DatabaseChoice.MULTI,
}

_SCALE_MAP = {
    "small (< 1k users)": ScaleExpectation.SMALL,
    "medium (1k – 100k users)": ScaleExpectation.MEDIUM,
    "large (100k – 1m users)": ScaleExpectation.LARGE,
    "massive (1m+ users)": ScaleExpectation.MASSIVE,
}

_DEPLOY_MAP = {
    "aws": DeploymentTarget.AWS,
    "google cloud (gcp)": DeploymentTarget.GCP,
    "azure": DeploymentTarget.AZURE,
    "on-premise": DeploymentTarget.ON_PREMISE,
    "hybrid": DeploymentTarget.HYBRID,
}

_EXTRA_FEATURES_LIST = [
    "Real-time / WebSockets",
    "Full-text Search",
    "File / Media Storage",
    "Notifications (push/email)",
    "Analytics / Monitoring",
    "Rate Limiting",
    "Background Jobs / Task Queue",
    "CDN for static assets",
]


def process_answer(state: SessionState, answer: str) -> SessionState:
    """Process the user's answer for the current step and return updated state."""
    step = state.current_step
    ans = answer.strip()

    if step == QuestionStep.APP_NAME:
        state.app_name = ans

    elif step == QuestionStep.APP_DESCRIPTION:
        state.app_description = ans

    elif step == QuestionStep.APP_TYPE:
        state.app_type = _APP_TYPE_MAP.get(ans.lower(), AppType.WEB_APP)

    elif step == QuestionStep.COMPLEXITY:
        state.complexity = _COMPLEXITY_MAP.get(ans.lower(), ComplexityLevel.STANDARD)

    elif step == QuestionStep.AUTH:
        state.auth_method = _AUTH_MAP.get(ans.lower(), AuthMethod.JWT)

    elif step == QuestionStep.DATABASE:
        state.database = _DB_MAP.get(ans.lower(), DatabaseChoice.POSTGRESQL)

    elif step == QuestionStep.SCALE:
        state.scale = _SCALE_MAP.get(ans.lower(), ScaleExpectation.MEDIUM)

    elif step == QuestionStep.DEPLOYMENT:
        state.deployment = _DEPLOY_MAP.get(ans.lower(), DeploymentTarget.AWS)

    elif step == QuestionStep.EXTRA_FEATURES:
        if ans.lower() == "none":
            state.extra_features = []
        else:
            features = []
            for part in ans.replace(",", " ").split():
                part = part.strip()
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(_EXTRA_FEATURES_LIST):
                        features.append(_EXTRA_FEATURES_LIST[idx])
            state.extra_features = features if features else []

    # Advance to next step
    state.current_step = _next_step(step)
    return state


def get_current_question(state: SessionState) -> AgentMessage:
    """Return the agent message for the current step."""
    generator = QUESTION_MAP.get(state.current_step)
    if generator is None:
        return AgentMessage(
            text="All requirements gathered! Generating your architecture diagram...",
            is_complete=True,
        )
    return generator()
