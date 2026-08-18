def build_portfolio_prompt(
    user_id: str,
    user_question: str,
) -> str:
    return f"""
User ID:
{user_id}

Manager question:
{user_question}

Retrieve only the relevant factual portfolio and
timesheet evidence needed to answer this question.

Use SharePoint and Dataverse tools only.

Return an evidence package.
Do not generate the final management answer.
"""


def build_engineering_prompt(
    user_id: str,
    user_question: str,
) -> str:
    return f"""
User ID:
{user_id}

Manager question:
{user_question}

Retrieve only the relevant engineering delivery
evidence and curated MAQ delivery guidance needed
to answer this question.

Use Azure DevOps and MAQ Delivery Knowledge only.

Return an evidence package.
Do not generate the final management answer.
"""


def build_analyst_prompt(
    user_question: str,
    portfolio_evidence: str,
    engineering_evidence: str,
    portfolio_status: str,
    engineering_status: str,
) -> str:
    return f"""
Manager question:
{user_question}

PORTFOLIO BRANCH STATUS:
{portfolio_status}

PORTFOLIO EVIDENCE:
{portfolio_evidence}

ENGINEERING BRANCH STATUS:
{engineering_status}

ENGINEERING EVIDENCE:
{engineering_evidence}

Produce the final management-facing response using
only the supplied evidence.

If a branch failed or returned no relevant evidence,
do not invent information from that branch.

Preserve deterministic classifications and clearly
separate factual evidence from recommendations.
"""
