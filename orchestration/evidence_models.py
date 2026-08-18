from pydantic import BaseModel, Field


class EvidenceSource(BaseModel):
    name: str
    available: bool = True


class PortfolioEvidence(BaseModel):
    branch: str = "portfolio"
    success: bool
    summary: str
    sources: list[str] = Field(default_factory=list)


class EngineeringEvidence(BaseModel):
    branch: str = "engineering"
    success: bool
    summary: str
    sources: list[str] = Field(default_factory=list)


class AnalystEvidencePackage(BaseModel):
    question: str

    portfolio_status: str
    portfolio_evidence: PortfolioEvidence | None = None

    engineering_status: str
    engineering_evidence: EngineeringEvidence | None = None