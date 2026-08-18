from connectors.sharepoint_export import get_projects
from connectors.dataverse_timeentry import get_project_timesheet_summary


def get_project_evidence(
    project_id: str,
) -> dict:
    """Combines SharePoint project status and live Dataverse timesheet signals."""

    projects = get_projects()

    project = next(
        (
            item
            for item in projects
            if item["project_id"].lower() == project_id.lower()
        ),
        None,
    )

    if not project:
        return {
            "success": False,
            "error": f"Project {project_id} was not found.",
        }

    timesheet_summary = get_project_timesheet_summary(
        project_id
    )

    return {
        "success": True,
        "project": project,
        "timesheet": timesheet_summary,
        "timesheet_source": "Dataverse",
    }