"""Worker Agent — generates Mermaid.js system design diagrams.

Takes the finalized SessionState from the Parent Agent and produces
a Mermaid diagram string at the requested complexity level.
"""

from __future__ import annotations

from app.models import (
    AppType,
    AuthMethod,
    ComplexityLevel,
    DatabaseChoice,
    DeploymentTarget,
    ScaleExpectation,
    SessionState,
)


# ── Helper labels ─────────────────────────────────────────────────────

_DB_LABEL = {
    DatabaseChoice.POSTGRESQL: "PostgreSQL",
    DatabaseChoice.MYSQL: "MySQL",
    DatabaseChoice.MONGODB: "MongoDB",
    DatabaseChoice.DYNAMODB: "DynamoDB",
    DatabaseChoice.REDIS: "Redis",
    DatabaseChoice.MULTI: "Multi-DB",
}

_DEPLOY_LABEL = {
    DeploymentTarget.AWS: "AWS Cloud",
    DeploymentTarget.GCP: "Google Cloud",
    DeploymentTarget.AZURE: "Azure Cloud",
    DeploymentTarget.ON_PREMISE: "On-Premise DC",
    DeploymentTarget.HYBRID: "Hybrid Cloud",
}

_AUTH_LABEL = {
    AuthMethod.JWT: "JWT Auth",
    AuthMethod.OAUTH2: "OAuth 2.0 / SSO",
    AuthMethod.SESSION: "Session Auth",
    AuthMethod.API_KEY: "API Key Auth",
    AuthMethod.NONE: "No Auth",
}


def _has_feature(state: SessionState, keyword: str) -> bool:
    return any(keyword.lower() in f.lower() for f in state.extra_features)


# ── Standard diagram ──────────────────────────────────────────────────

def _build_standard(s: SessionState) -> str:
    db = _DB_LABEL.get(s.database, "Database")
    auth = _AUTH_LABEL.get(s.auth_method, "Auth")
    deploy = _DEPLOY_LABEL.get(s.deployment, "Cloud")

    lines = [
        "graph TB",
        f'    subgraph "{deploy}"',
    ]

    # Client tier
    if s.app_type in (AppType.WEB_APP, AppType.ECOMMERCE, AppType.SOCIAL_PLATFORM, AppType.SAAS_PLATFORM):
        lines.append('        CLIENT["🌐 Web Browser"]')
    elif s.app_type == AppType.MOBILE_APP:
        lines.append('        CLIENT["📱 Mobile App"]')
    elif s.app_type == AppType.IOT_PLATFORM:
        lines.append('        CLIENT["📡 IoT Devices"]')
    else:
        lines.append('        CLIENT["👤 API Client"]')

    # Server
    lines.append(f'        SERVER["🖥️ {s.app_name or "App"} Server"]')

    # Auth
    if s.auth_method and s.auth_method != AuthMethod.NONE:
        lines.append(f'        AUTH["{auth}"]')
        lines.append("        CLIENT -->|Request| AUTH")
        lines.append("        AUTH -->|Validated| SERVER")
    else:
        lines.append("        CLIENT -->|Request| SERVER")

    # Database
    lines.append(f'        DB[("💾 {db}")]')
    lines.append("        SERVER -->|Read/Write| DB")

    # Optional features
    if _has_feature(s, "file") or _has_feature(s, "media"):
        lines.append('        STORAGE["📁 File Storage"]')
        lines.append("        SERVER -->|Upload/Download| STORAGE")

    if _has_feature(s, "notification"):
        lines.append('        NOTIFY["🔔 Notification Service"]')
        lines.append("        SERVER -->|Send| NOTIFY")

    lines.append("    end")

    # Styling
    lines += [
        "    style CLIENT fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style SERVER fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style DB fill:#FFB347,stroke:#CC8400,color:#333",
    ]
    if s.auth_method and s.auth_method != AuthMethod.NONE:
        lines.append("    style AUTH fill:#FF6B6B,stroke:#CC4444,color:#fff")

    return "\n".join(lines)


# ── Complex diagram ───────────────────────────────────────────────────

def _build_complex(s: SessionState) -> str:
    db = _DB_LABEL.get(s.database, "Database")
    auth = _AUTH_LABEL.get(s.auth_method, "Auth")
    deploy = _DEPLOY_LABEL.get(s.deployment, "Cloud")

    lines = [
        "graph TB",
        # Client layer
        '    subgraph "Client Tier"',
    ]

    if s.app_type in (AppType.WEB_APP, AppType.ECOMMERCE, AppType.SOCIAL_PLATFORM, AppType.SAAS_PLATFORM):
        lines.append('        WEB["🌐 Web App<br/>React / Next.js"]')
        lines.append('        MOBILE["📱 Mobile App"]')
    elif s.app_type == AppType.MOBILE_APP:
        lines.append('        MOBILE["📱 Mobile App<br/>iOS / Android"]')
        lines.append('        WEB["🌐 Admin Portal"]')
    elif s.app_type == AppType.IOT_PLATFORM:
        lines.append('        IOT["📡 IoT Devices"]')
        lines.append('        WEB["🌐 Dashboard"]')
    else:
        lines.append('        WEB["👤 API Consumers"]')
    lines.append("    end")

    # CDN
    if _has_feature(s, "cdn"):
        lines.append('    CDN["🌍 CDN<br/>CloudFront / Cloudflare"]')

    # Gateway & Auth
    lines.append(f"""
    subgraph "API Gateway & Security"
        LB["⚖️ Load Balancer"]
        GW["🚪 API Gateway"]
        AUTH["{auth}"]
    end""")

    # Microservices
    lines.append(f"""
    subgraph "Application Services"
        SVC1["⚙️ Core Service<br/>{s.app_name or 'App'} Logic"]
        SVC2["👤 User Service"]
        SVC3["📊 Data Service"]
    end""")

    # Data tier
    db_extra = ""
    if s.database == DatabaseChoice.MULTI:
        db_extra = f"""
        DB1[("💾 PostgreSQL<br/>Primary")]
        DB2[("💾 MongoDB<br/>Documents")]"""
    else:
        db_extra = f"""
        DB1[("💾 {db}<br/>Primary")]"""

    lines.append(f"""
    subgraph "Data Tier"
        CACHE["⚡ Redis Cache"]{db_extra}
    end""")

    # Message queue
    lines.append("""
    subgraph "Async Processing"
        MQ["📨 Message Queue<br/>RabbitMQ / SQS"]
        WORKER["🔧 Background Workers"]
    end""")

    # Monitoring
    lines.append("""
    subgraph "Observability"
        LOG["📋 Logging<br/>ELK / CloudWatch"]
        MON["📈 Monitoring<br/>Prometheus / Grafana"]
    end""")

    # Connections
    if s.app_type in (AppType.WEB_APP, AppType.ECOMMERCE, AppType.SOCIAL_PLATFORM, AppType.SAAS_PLATFORM):
        if _has_feature(s, "cdn"):
            lines.append("    WEB --> CDN --> LB")
        else:
            lines.append("    WEB --> LB")
        lines.append("    MOBILE --> LB")
    elif s.app_type == AppType.MOBILE_APP:
        lines.append("    MOBILE --> LB")
        lines.append("    WEB --> LB")
    elif s.app_type == AppType.IOT_PLATFORM:
        lines.append("    IOT --> LB")
        lines.append("    WEB --> LB")
    else:
        lines.append("    WEB --> LB")

    lines += [
        "    LB --> GW",
        "    GW --> AUTH",
        "    AUTH --> SVC1",
        "    AUTH --> SVC2",
        "    AUTH --> SVC3",
        "    SVC1 --> CACHE",
        "    SVC1 --> DB1",
        "    SVC2 --> DB1",
        "    SVC3 --> DB1",
        "    SVC1 --> MQ",
        "    MQ --> WORKER",
    ]

    if s.database == DatabaseChoice.MULTI:
        lines.append("    SVC3 --> DB2")

    # Optional features
    if _has_feature(s, "file") or _has_feature(s, "media"):
        lines.append('    S3["📁 Object Storage<br/>S3 / GCS"]')
        lines.append("    SVC1 --> S3")

    if _has_feature(s, "search"):
        lines.append('    ES["🔍 Search Engine<br/>Elasticsearch"]')
        lines.append("    SVC3 --> ES")

    if _has_feature(s, "real-time") or _has_feature(s, "websocket"):
        lines.append('    WS["🔌 WebSocket Server"]')
        lines.append("    GW --> WS")

    if _has_feature(s, "notification"):
        lines.append('    NOTIFY["🔔 Notification Service<br/>SNS / FCM"]')
        lines.append("    WORKER --> NOTIFY")

    lines += [
        "    SVC1 -.-> LOG",
        "    SVC1 -.-> MON",
    ]

    # Styling
    lines += [
        "    style LB fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style GW fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style AUTH fill:#FF6B6B,stroke:#CC4444,color:#fff",
        "    style SVC1 fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC2 fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC3 fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style CACHE fill:#FFD700,stroke:#CC9900,color:#333",
        "    style DB1 fill:#FFB347,stroke:#CC8400,color:#333",
        "    style MQ fill:#DDA0DD,stroke:#993399,color:#333",
        "    style WORKER fill:#DDA0DD,stroke:#993399,color:#333",
    ]

    return "\n".join(lines)


# ── Highly complex diagram ────────────────────────────────────────────

def _build_highly_complex(s: SessionState) -> str:
    db = _DB_LABEL.get(s.database, "Database")
    auth = _AUTH_LABEL.get(s.auth_method, "Auth")
    deploy = _DEPLOY_LABEL.get(s.deployment, "Cloud")

    lines = [
        "graph TB",
        # Client layer
        '    subgraph "Client Tier"',
        '        WEB["🌐 Web App<br/>React / Next.js<br/>SSR + PWA"]',
        '        MOBILE["📱 Mobile<br/>iOS / Android"]',
        '        SDK["🔗 Partner SDKs"]',
        '        IOT_D["📡 IoT Devices"]',
        "    end",
        "",
        # Edge
        '    subgraph "Edge Layer"',
        '        CDN["🌍 CDN<br/>Multi-Region"]',
        '        WAF["🛡️ WAF / DDoS<br/>Protection"]',
        '        EDGE_FN["⚡ Edge Functions<br/>Lambda@Edge"]',
        "    end",
        "",
        # Gateway
        f'    subgraph "API Gateway & Identity"',
        '        GLB["⚖️ Global Load Balancer"]',
        '        GW["🚪 API Gateway<br/>Rate Limiting + Throttle"]',
        f'        AUTH["{auth}<br/>+ MFA"]',
        '        RBAC["🔐 RBAC / ABAC<br/>Policy Engine"]',
        "    end",
        "",
        # Service mesh
        f'    subgraph "Service Mesh — {deploy}"',
        '        MESH["🕸️ Service Mesh<br/>Istio / Linkerd"]',
        "",
        f'        subgraph "Domain: Core"',
        f'            SVC_CORE["⚙️ {s.app_name or "App"} Core<br/>Service"]',
        '            SVC_USER["👤 User<br/>Service"]',
        '            SVC_BILLING["💳 Billing<br/>Service"]',
        "        end",
        "",
        '        subgraph "Domain: Data"',
        '            SVC_DATA["📊 Data<br/>Service"]',
        '            SVC_SEARCH["🔍 Search<br/>Service"]',
        '            SVC_ANALYTICS["📈 Analytics<br/>Service"]',
        "        end",
        "",
        '        subgraph "Domain: Communication"',
        '            SVC_NOTIFY["🔔 Notification<br/>Service"]',
        '            SVC_RT["🔌 Real-time<br/>WebSocket Server"]',
        '            SVC_EMAIL["✉️ Email<br/>Service"]',
        "        end",
        "    end",
        "",
        # Event bus
        '    subgraph "Event-Driven Backbone"',
        '        KAFKA["📨 Event Bus<br/>Kafka / EventBridge"]',
        '        SCHEMA_REG["📋 Schema Registry"]',
        '        DLQ["⚠️ Dead Letter Queue"]',
        "    end",
        "",
        # Async
        '    subgraph "Async Processing"',
        '        SAGA["🔄 Saga<br/>Orchestrator"]',
        '        WORKERS["🔧 Worker Fleet<br/>Auto-scaling"]',
        '        SCHEDULER["⏰ Job Scheduler<br/>Cron / Airflow"]',
        "    end",
        "",
    ]

    # Data tier — depends on DB choice
    if s.database == DatabaseChoice.MULTI:
        lines += [
            '    subgraph "Data Tier — Polyglot Persistence"',
            '        PG[("💾 PostgreSQL<br/>Transactional")]',
            '        MONGO[("📄 MongoDB<br/>Documents")]',
            '        REDIS["⚡ Redis Cluster<br/>Cache + Sessions"]',
            '        ES["🔍 Elasticsearch<br/>Full-text"]',
            '        TS[("📊 TimescaleDB<br/>Time-series")]',
            "    end",
        ]
    else:
        lines += [
            '    subgraph "Data Tier"',
            f'        PRIMARY[("💾 {db}<br/>Primary + Replicas")]',
            '        REDIS["⚡ Redis Cluster<br/>Cache + Sessions"]',
            '        ES["🔍 Elasticsearch<br/>Full-text"]',
            f'        READ_REPLICA[("📖 {db}<br/>Read Replicas")]',
            "    end",
        ]

    # Storage
    lines += [
        "",
        '    subgraph "Object Storage"',
        '        S3["📁 Object Storage<br/>S3 / GCS"]',
        '        MEDIA["🖼️ Media Pipeline<br/>Transcode + Optimize"]',
        "    end",
        "",
    ]

    # Observability
    lines += [
        '    subgraph "Observability & Operations"',
        '        PROM["📈 Prometheus<br/>+ Grafana"]',
        '        TRACE["🔭 Distributed Tracing<br/>Jaeger / X-Ray"]',
        '        LOG["📋 Centralized Logging<br/>ELK Stack"]',
        '        ALERT["🚨 Alerting<br/>PagerDuty / OpsGenie"]',
        '        CHAOS["🐒 Chaos Engineering"]',
        "    end",
        "",
    ]

    # CI/CD
    lines += [
        '    subgraph "CI/CD & Infrastructure"',
        '        CICD["🚀 CI/CD Pipeline<br/>GitHub Actions"]',
        '        IAC["🏗️ IaC<br/>Terraform / Pulumi"]',
        '        REGISTRY["📦 Container<br/>Registry"]',
        '        K8S["☸️ Kubernetes<br/>Multi-cluster"]',
        "    end",
        "",
    ]

    # Connections — edge
    lines += [
        "    WEB --> CDN",
        "    MOBILE --> CDN",
        "    SDK --> WAF",
        "    IOT_D --> WAF",
        "    CDN --> WAF",
        "    WAF --> EDGE_FN",
        "    EDGE_FN --> GLB",
        "",
        "    GLB --> GW",
        "    GW --> AUTH",
        "    AUTH --> RBAC",
        "    RBAC --> MESH",
        "",
    ]

    # Mesh to services
    lines += [
        "    MESH --> SVC_CORE",
        "    MESH --> SVC_USER",
        "    MESH --> SVC_BILLING",
        "    MESH --> SVC_DATA",
        "    MESH --> SVC_SEARCH",
        "    MESH --> SVC_ANALYTICS",
        "    MESH --> SVC_NOTIFY",
        "    MESH --> SVC_RT",
        "    MESH --> SVC_EMAIL",
        "",
    ]

    # Services to event bus
    lines += [
        "    SVC_CORE --> KAFKA",
        "    SVC_USER --> KAFKA",
        "    SVC_BILLING --> KAFKA",
        "    SVC_DATA --> KAFKA",
        "    KAFKA --> SCHEMA_REG",
        "    KAFKA --> DLQ",
        "",
        "    KAFKA --> SAGA",
        "    SAGA --> WORKERS",
        "    SCHEDULER --> WORKERS",
        "",
    ]

    # Services to data
    if s.database == DatabaseChoice.MULTI:
        lines += [
            "    SVC_CORE --> PG",
            "    SVC_USER --> PG",
            "    SVC_BILLING --> PG",
            "    SVC_DATA --> MONGO",
            "    SVC_SEARCH --> ES",
            "    SVC_ANALYTICS --> TS",
            "    SVC_CORE --> REDIS",
        ]
    else:
        lines += [
            "    SVC_CORE --> PRIMARY",
            "    SVC_USER --> PRIMARY",
            "    SVC_BILLING --> PRIMARY",
            "    SVC_DATA --> READ_REPLICA",
            "    SVC_SEARCH --> ES",
            "    SVC_CORE --> REDIS",
        ]

    lines += [
        "",
        "    SVC_DATA --> S3",
        "    S3 --> MEDIA",
        "",
        "    SVC_NOTIFY --> WORKERS",
        "    SVC_EMAIL --> WORKERS",
        "",
        # Observability connections
        "    MESH -.-> PROM",
        "    MESH -.-> TRACE",
        "    MESH -.-> LOG",
        "    PROM -.-> ALERT",
        "",
        # CI/CD connections
        "    CICD --> REGISTRY",
        "    REGISTRY --> K8S",
        "    IAC --> K8S",
        "",
    ]

    # Styling
    lines += [
        "    style CDN fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style WAF fill:#FF6B6B,stroke:#CC4444,color:#fff",
        "    style GLB fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style GW fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    style AUTH fill:#FF6B6B,stroke:#CC4444,color:#fff",
        "    style RBAC fill:#FF6B6B,stroke:#CC4444,color:#fff",
        "    style MESH fill:#9B59B6,stroke:#7D3C98,color:#fff",
        "    style SVC_CORE fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_USER fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_BILLING fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_DATA fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_SEARCH fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_ANALYTICS fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_NOTIFY fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_RT fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style SVC_EMAIL fill:#50C878,stroke:#2E8B57,color:#fff",
        "    style KAFKA fill:#DDA0DD,stroke:#993399,color:#333",
        "    style REDIS fill:#FFD700,stroke:#CC9900,color:#333",
        "    style K8S fill:#326CE5,stroke:#1A3A7A,color:#fff",
    ]

    return "\n".join(lines)


# ── Public entry point ────────────────────────────────────────────────

def generate_diagram(state: SessionState) -> str:
    """Generate a Mermaid diagram based on the session state."""
    builders = {
        ComplexityLevel.STANDARD: _build_standard,
        ComplexityLevel.COMPLEX: _build_complex,
        ComplexityLevel.HIGHLY_COMPLEX: _build_highly_complex,
    }
    builder = builders.get(state.complexity, _build_standard)
    return builder(state)


def generate_summary(state: SessionState) -> str:
    """Generate a human-readable summary of the architecture."""
    db = _DB_LABEL.get(state.database, "Database")
    auth = _AUTH_LABEL.get(state.auth_method, "Auth")
    deploy = _DEPLOY_LABEL.get(state.deployment, "Cloud")
    complexity_label = {
        ComplexityLevel.STANDARD: "Standard",
        ComplexityLevel.COMPLEX: "Complex (Microservices)",
        ComplexityLevel.HIGHLY_COMPLEX: "Highly Complex (Distributed)",
    }

    lines = [
        f"## System Design: {state.app_name}",
        "",
        f"**Description:** {state.app_description}",
        "",
        "### Architecture Decisions",
        "",
        f"| Attribute | Choice |",
        f"|-----------|--------|",
        f"| Complexity | {complexity_label.get(state.complexity, 'Standard')} |",
        f"| Authentication | {auth} |",
        f"| Database | {db} |",
        f"| Deployment | {deploy} |",
        f"| Scale | {state.scale.value if state.scale else 'N/A'} |",
    ]

    if state.extra_features:
        lines.append(f"| Extra Features | {', '.join(state.extra_features)} |")

    lines += [
        "",
        "### Key Components",
        "",
    ]

    if state.complexity == ComplexityLevel.STANDARD:
        lines += [
            "- **Client Layer** — Single-page app or mobile client",
            f"- **Application Server** — Monolithic {state.app_name} server",
            f"- **Database** — {db} for persistence",
        ]
    elif state.complexity == ComplexityLevel.COMPLEX:
        lines += [
            "- **Client Layer** — Web + Mobile clients",
            "- **API Gateway** — Request routing, rate limiting",
            f"- **Microservices** — Core, User, and Data services",
            f"- **Cache** — Redis for performance",
            f"- **Database** — {db} for persistence",
            "- **Message Queue** — Async processing",
            "- **Observability** — Logging + Monitoring",
        ]
    else:
        lines += [
            "- **Edge Layer** — CDN, WAF, Edge functions",
            "- **API Gateway** — Global LB + Gateway + Auth + RBAC",
            "- **Service Mesh** — Istio/Linkerd with 9 microservices",
            "- **Event Bus** — Kafka with schema registry + DLQ",
            "- **Saga Orchestration** — Distributed transactions",
            f"- **Data Tier** — {db} + Redis + Elasticsearch",
            "- **Object Storage** — S3/GCS with media pipeline",
            "- **Observability** — Prometheus, Jaeger, ELK, Alerting, Chaos Engineering",
            "- **CI/CD** — GitOps with Kubernetes multi-cluster",
        ]

    return "\n".join(lines)
