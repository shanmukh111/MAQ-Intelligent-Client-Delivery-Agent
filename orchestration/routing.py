def route_question(
    user_question: str,
) -> dict:
    """
    Deterministically decides which evidence
    branches are relevant to the question.
    """

    question = user_question.lower()

    portfolio_terms = {
        "project",
        "projects",
        "portfolio",
        "power bi",
        "d365",
        "dynamics",
        "budget",
        "schedule",
        "milestone",
        "timesheet",
        "timesheets",
        "utilization",
        "variance",
    }

    engineering_terms = {
        "sprint",
        "iteration",
        "work item",
        "work items",
        "azure devops",
        "engineering",
        "backlog",
        "completion",
        "delivery gap",
    }

    recommendation_terms = {
        "recommend",
        "recommendation",
        "recommendations",
        "management action",
        "management actions",
        "prioritize",
        "mitigation",
        "what should",
    }

    use_portfolio = any(
        term in question
        for term in portfolio_terms
    )

    use_engineering = any(
        term in question
        for term in engineering_terms
    )

    wants_guidance = any(
        term in question
        for term in recommendation_terms
    )

    if not use_portfolio and not use_engineering:
        use_portfolio = True
        use_engineering = True

    return {
        "portfolio": use_portfolio,
        "engineering": use_engineering,
        "guidance": wants_guidance,
    }


def route_devops_tools(
    user_question: str,
) -> list[str]:
    """
    Select the minimum Azure DevOps MCP tool set
    required for the engineering question.
    """

    question = user_question.lower()

    # Sprint health / progress questions
    if (
        "sprint" in question
        or "sprint health" in question
        or "delivery gap" in question
        or "completion" in question
    ):
        return [
            "get_current_sprint_summary",
        ]

    # Work-item / backlog questions
    if (
        "work item" in question
        or "work items" in question
        or "backlog" in question
    ):
        return [
            "get_active_work_items",
        ]

    # Iteration questions
    if (
        "iteration" in question
        or "iterations" in question
    ):
        return [
            "get_iterations",
        ]

    # General Azure DevOps/project information
    return [
        "get_project_info",
    ]