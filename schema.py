"""Structured schema for a single app's research finding.

The controlled vocabularies (Enums) are the backbone of the whole project: they
let us cluster 100 apps into patterns instead of eyeballing free text, and they
make the agent's output machine-checkable in the verification loop.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AuthMethod(str, Enum):
    oauth2 = "OAuth2"
    api_key = "API key"
    basic = "Basic"
    token = "Token"          # personal access / bearer token, not a full OAuth flow
    other = "Other"
    none = "None / n/a"      # no public programmatic auth (e.g. CLI-only, no API)


class AccessModel(str, Enum):
    """Can a developer get working credentials themselves?"""
    self_serve_free = "Self-serve free"        # sign up, get a key, free tier
    self_serve_trial = "Self-serve trial"      # self-serve but time/− limited trial
    paid_plan = "Paid plan required"           # need to pay to get API access at all
    admin_approval = "Admin / app review"      # self-serve start but gated by app review
    partner_gated = "Partner / contact-sales"  # partnership or sales gate, no self-serve
    unknown = "Unknown"


class Buildability(str, Enum):
    ready = "Ready"                 # could ship an agent toolkit today, self-serve
    ready_gated = "Ready but gated" # API is fine but credentials need approval/partnership
    partial = "Partial"             # API exists but narrow / awkward for agents
    blocked = "Blocked"             # no usable public API, or hard partner gate
    unknown = "Unknown"


class MCPStatus(str, Enum):
    official = "Official MCP"       # vendor ships an MCP server
    community = "Community MCP"     # third-party MCP exists
    none = "No MCP"
    unknown = "Unknown"


class AppFinding(BaseModel):
    id: int
    name: str
    category: str
    hint: str = ""

    one_liner: str = Field(..., description="What it does, one line.")
    auth_methods: List[AuthMethod] = Field(default_factory=list)
    auth_detail: str = Field("", description="Free-text nuance, e.g. 'OAuth2 + API key for server-to-server'.")

    access_model: AccessModel = AccessModel.unknown
    access_detail: str = ""

    api_surface: str = Field("", description="REST/GraphQL? Rough breadth.")
    api_breadth: str = Field("", description="one of: broad | moderate | narrow | none")
    mcp: MCPStatus = MCPStatus.unknown

    buildability: Buildability = Buildability.unknown
    blocker: str = Field("", description="Main blocker if not Ready. Empty if Ready.")

    evidence_url: str = Field("", description="The doc/article behind the answer.")
    composio_supported: Optional[bool] = Field(
        None, description="Does Composio already ship a toolkit? Cross-check signal."
    )

    confidence: float = Field(0.5, ge=0, le=1, description="Agent self-rated confidence.")
    notes: str = ""

    # Verification bookkeeping (filled by verify.py)
    verified: bool = False
    verify_changed: Optional[List[str]] = None   # fields corrected in the critic pass


class Dataset(BaseModel):
    findings: List[AppFinding]
