from connectors.dataverse_timeentry import (
    get_project_timesheet_summary,
)

from retrieval.hybrid_rag import (
    search_delivery_knowledge as hybrid_search_delivery_knowledge,
)


def build_delivery_tools(
    projects: list[dict],
    mark_source,
):
    """
    Build request-scoped MAF tools.

    The SharePoint project collection belongs to the
    current HTTP request, so these tools intentionally
    close over that request's project data.
    """

    # -----------------------------------------------------
    # TOOL 1
    # SharePoint project search
    # -----------------------------------------------------

    def get_projects(
        technology: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        """
        Returns projects from the live SharePoint
        project register.

        Optionally filters by technology and status.
        """

        mark_source("SharePoint")

        results = projects

        if technology:

            technology_normalized = (
                technology.strip().lower()
            )

            results = [
                project
                for project in results
                if str(
                    project.get(
                        "Technology",
                        "",
                    )
                ).strip().lower()
                == technology_normalized
            ]

        if status:

            status_normalized = (
                status.strip().lower()
            )

            results = [
                project
                for project in results
                if str(
                    project.get(
                        "Status",
                        "",
                    )
                ).strip().lower()
                == status_normalized
            ]

        return results


    # -----------------------------------------------------
    # TOOL 2
    # Deterministic risk filtering
    # -----------------------------------------------------

    def get_at_risk_projects(
        technology: str | None = None,
    ) -> list[dict]:
        """
        Returns active projects where either
        schedule or budget is At Risk or Behind.
        """

        mark_source("SharePoint")

        active_projects = get_projects(
            technology=technology,
            status="Active",
        )

        results = []

        for project in active_projects:

            schedule_status = str(
                project.get(
                    "Schedule Status",
                    "",
                )
            ).strip().lower()

            budget_status = str(
                project.get(
                    "Budget Status",
                    "",
                )
            ).strip().lower()

            if (
                schedule_status
                in {
                    "at risk",
                    "behind",
                }
                or
                budget_status
                in {
                    "at risk",
                    "behind",
                }
            ):
                results.append(
                    project
                )

        return results


    # -----------------------------------------------------
    # TOOL 3
    # SharePoint + Dataverse
    # -----------------------------------------------------

    def get_project_delivery_evidence(
        project_id: str,
    ) -> dict:
        """
        Returns project information plus live
        Dataverse timesheet evidence.
        """

        mark_source("SharePoint")

        normalized_project_id = (
            project_id.strip().lower()
        )

        project = next(
            (
                item
                for item in projects
                if str(
                    item.get(
                        "Project ID",
                        "",
                    )
                ).strip().lower()
                == normalized_project_id
            ),
            None,
        )

        if project is None:

            return {
                "success": False,
                "error": (
                    f"Project {project_id} "
                    "was not found."
                ),
            }

        mark_source("Dataverse")

        timesheet = (
            get_project_timesheet_summary(
                project_id
            )
        )

        return {
            "success": True,
            "project": project,
            "timesheet": timesheet,
            "sources": [
                "SharePoint",
                "Dataverse",
            ],
        }


    # -----------------------------------------------------
    # TOOL 4
    # Hybrid RAG
    # -----------------------------------------------------

    def search_delivery_knowledge(
        query: str,
        top_k: int = 3,
    ) -> dict:
        """
        Searches curated MAQ delivery knowledge
        through Hybrid RAG.

        Use for management guidance,
        delivery-risk interpretation,
        timesheet interpretation,
        Power BI, Azure, D365, and sprint guidance.

        Do not use this as a substitute for live
        project evidence.
        """

        mark_source(
            "MAQ Delivery Knowledge"
        )

        return (
            hybrid_search_delivery_knowledge(
                query=query,
                top_k=top_k,
            )
        )


    return [
        get_projects,
        get_at_risk_projects,
        get_project_delivery_evidence,
        search_delivery_knowledge,
    ]