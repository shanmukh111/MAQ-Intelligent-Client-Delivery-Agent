from connectors.dataverse_timeentry import (
    get_project_timesheet_summary,
)


def build_portfolio_tools(
    projects: list[dict],
    mark_source,
):
    """
    Build request-scoped tools for the
    MAQPortfolioEvidenceAgent.

    Sources:
    - SharePoint
    - Dataverse
    """

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


    def get_at_risk_projects(
        technology: str | None = None,
    ) -> list[dict]:
        """
        Returns active projects where either
        Schedule Status or Budget Status is
        At Risk or Behind.
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
                results.append(project)

        return results


    def get_project_delivery_evidence(
        project_id: str,
    ) -> dict:
        """
        Returns SharePoint project evidence
        plus live Dataverse timesheet evidence.
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


    return [
        get_projects,
        get_at_risk_projects,
        get_project_delivery_evidence,
    ]