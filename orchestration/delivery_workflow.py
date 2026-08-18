import asyncio
from collections.abc import Awaitable, Callable

from agent_framework import (
    FunctionInvocationContext,
    MCPStdioTool,
)

from orchestration.routing import (
    route_question,
)

from orchestration.evidence_models import (
    PortfolioEvidence,
    EngineeringEvidence,
)

from orchestration.evidence_validation import (
    run_with_single_retry,
)

from orchestration.prompts import (
    build_analyst_prompt,
    build_engineering_prompt,
    build_portfolio_prompt,
)

from agents.analyst_agent import (
    create_analyst_agent,
)

from agents.engineering_agent import (
    create_engineering_agent,
)

from agents.engineering_tools import (
    build_engineering_tools,
)

from agents.portfolio_agent import (
    create_portfolio_agent,
)

from agents.portfolio_tools import (
    build_portfolio_tools,
)

from security.authorization import (
    authorize_route,
    AuthorizationError,
)


AZURE_DEVOPS_TOOLS = {
    "get_project_info",
    "get_active_work_items",
    "get_iterations",
    "get_current_sprint_summary",
}


async def run_delivery_workflow(
    *,
    user_id: str,
    user_question: str,
    projects: list[dict],
    mark_source,
) -> dict:
    """
    Executes the MAQ three-agent workflow.

    Flow:

        Portfolio Agent  ─┐
                          ├─ parallel
        Engineering Agent ┘
                ↓
        validation / retry
                ↓
        Analyst Agent
                ↓
        final management response
    """

    # -----------------------------------------------------
    # Deterministic routing
    # -----------------------------------------------------

    routing = route_question(
        user_question
    )

    print(
        "[Workflow] Routing decision:",
        routing,
    )

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    try:
        access = authorize_route(
            user_id=user_id,
            routing=routing,
        )

        print(
            "[Security] Authorized:",
            {
                "user_id": access.user_id,
                "role": access.role,
            },
        )

    except AuthorizationError as exc:

        print(
            "[Security] Authorization denied:",
            str(exc),
        )

        raise


    # -----------------------------------------------------
    # Request-scoped tools
    # -----------------------------------------------------

    portfolio_tools = (
        build_portfolio_tools(
            projects=projects,
            mark_source=mark_source,
        )
    )

    # Hybrid RAG is exposed to the Engineering Agent
    # only when the router determines guidance is needed.
    engineering_tools = []

    if routing["guidance"]:
        engineering_tools = (
            build_engineering_tools(
                mark_source=mark_source,
            )
        )


    # -----------------------------------------------------
    # Azure DevOps source tracking middleware
    # -----------------------------------------------------

    async def track_engineering_tool_usage(
        context: FunctionInvocationContext,
        call_next:
            Callable[
                [],
                Awaitable[None],
            ],
    ) -> None:

        tool_name = (
            context.function.name
        )

        print(
            "[ToolTracking] "
            f"Engineering called: {tool_name}"
        )

        normalized_name = (
            tool_name.lower()
        )

        is_azure_devops_tool = (
            "azure_devops"
            in normalized_name
            or any(
                tool_name_item
                in normalized_name
                for tool_name_item
                in AZURE_DEVOPS_TOOLS
            )
        )

        if is_azure_devops_tool:
            mark_source(
                "Azure DevOps"
            )

        # Execute the tool normally.
        await call_next()

        # Azure DevOps MCP tools are single-use within one agent run.
        #
        # This preserves MCP/autonomous tool selection, but prevents the
        # function-invocation loop from requesting the exact same live
        # Azure DevOps operation repeatedly after it already returned.
        #
        # FunctionInvocationContext.remove_tools(...) updates the live tool
        # list for the NEXT model/tool iteration.
        if is_azure_devops_tool:
            context.remove_tools(
                [tool_name]
            )

            print(
                "[ToolControl] Removed single-use "
                f"Azure DevOps tool: {tool_name}"
            )


    # -----------------------------------------------------
    # Azure DevOps MCP lifetime
    # -----------------------------------------------------

    async with MCPStdioTool(
        name="azure_devops",
        command="python",
        args=[
            "mcp_server/devops_server.py"
        ],
    ) as devops_mcp:
        # -------------------------------------------------
        # Create Agent 1 + Agent 2
        # -------------------------------------------------

        async with (
            create_portfolio_agent()
        ) as portfolio_agent:

            async with (
                create_engineering_agent(
                    middleware=[
                        track_engineering_tool_usage,
                    ],
                )
            ) as engineering_agent:

                async def run_portfolio():
                    """
                    Portfolio branch.
                    """

                    prompt = build_portfolio_prompt(
                        user_id=user_id,
                        user_question=user_question,
                    )

                    return await portfolio_agent.run(
                        prompt,
                        tools=portfolio_tools,
                        options={
                            "response_format": PortfolioEvidence,
                        },
                    )


                async def run_engineering():
                    """
                    Engineering branch.
                    """

                    prompt = build_engineering_prompt(
                        user_id=user_id,
                        user_question=user_question,
                    )

                    return await engineering_agent.run(
                        prompt,
                        tools=[
                            devops_mcp,
                            *engineering_tools,
                        ],
                        options={
                            "response_format": EngineeringEvidence,
                        },
                    )


                # -----------------------------------------
                # CONDITIONAL ROUTING
                # -----------------------------------------

                portfolio_result = {
                    "success": False,
                    "status": "skipped",
                    "text": (
                        "Portfolio evidence branch was "
                        "not required for this question."
                    ),
                    "attempts": 0,
                }

                engineering_result = {
                    "success": False,
                    "status": "skipped",
                    "text": (
                        "Engineering evidence branch was "
                        "not required for this question."
                    ),
                    "attempts": 0,
                }


                # -----------------------------------------
                # BOTH BRANCHES → RUN IN PARALLEL
                # -----------------------------------------

                if (
                    routing["portfolio"]
                    and routing["engineering"]
                ):

                    print(
                        "[Workflow] Starting Portfolio "
                        "and Engineering agents "
                        "in parallel..."
                    )

                    (
                        portfolio_result,
                        engineering_result,
                    ) = await asyncio.gather(
                        run_with_single_retry(
                            run_portfolio,
                            "Portfolio Agent",
                            PortfolioEvidence,
                        ),
                        run_with_single_retry(
                            run_engineering,
                            "Engineering Agent",
                            EngineeringEvidence,
                        ),
                    )

                    print(
                        "[Workflow] Parallel evidence "
                        "stage complete."
                    )


                # -----------------------------------------
                # PORTFOLIO ONLY
                # -----------------------------------------

                elif routing["portfolio"]:

                    print(
                        "[Workflow] Portfolio branch only."
                    )

                    portfolio_result = (
                        await run_with_single_retry(
                            run_portfolio,
                            "Portfolio Agent",
                            PortfolioEvidence,
                        )
                    )


                # -----------------------------------------
                # ENGINEERING ONLY
                # -----------------------------------------

                elif routing["engineering"]:

                    print(
                        "[Workflow] Engineering branch only."
                    )

                    engineering_result = (
                        await run_with_single_retry(
                            run_engineering,
                            "Engineering Agent",
                            EngineeringEvidence,
                        )
                    )


    # -----------------------------------------------------
    # Evidence validation summary
    # -----------------------------------------------------

    portfolio_status = (
        portfolio_result["status"]
    )

    engineering_status = (
        engineering_result["status"]
    )

    print(
        "[Workflow] Portfolio status:",
        portfolio_status,
    )

    print(
        "[Workflow] Engineering status:",
        engineering_status,
    )


    # -----------------------------------------------------
    # At least one branch must succeed
    # -----------------------------------------------------

    available_results = [
        result
        for result in [
            portfolio_result,
            engineering_result,
        ]
        if result["status"] != "skipped"
    ]

    if (
        not available_results
        or not any(
            result["success"]
            for result in available_results
        )
    ):
        raise RuntimeError(
            "All required evidence branches failed."
        )


    # -----------------------------------------------------
    # Agent 3 — Analyst
    # -----------------------------------------------------

    analyst_prompt = (
        build_analyst_prompt(
            user_question=user_question,
            portfolio_evidence=
                portfolio_result["text"],
            engineering_evidence=
                engineering_result["text"],
            portfolio_status=
                portfolio_status,
            engineering_status=
                engineering_status,
        )
    )

    print(
        "[Workflow] Starting "
        "Delivery Analyst Agent..."
    )

    async with (
        create_analyst_agent()
    ) as analyst_agent:

        analyst_response = (
            await analyst_agent.run(
                analyst_prompt
            )
        )

    print(
        "[Workflow] Analyst Agent complete."
    )


    # -----------------------------------------------------
    # Workflow result
    # -----------------------------------------------------

    return {
        "success": True,
        "answer": analyst_response.text,

        "workflow": {
            "strategy": (
                "parallel-fan-out-fan-in"
            ),
            "portfolio_agent": {
                "status":
                    portfolio_status,
                "attempts":
                    portfolio_result[
                        "attempts"
                    ],
            },
            "engineering_agent": {
                "status":
                    engineering_status,
                "attempts":
                    engineering_result[
                        "attempts"
                    ],
            },
            "analyst_agent": {
                "status": "success",
            },
        },
    }