import csv
from pathlib import Path


DATA_FILE = Path("data/sharepoint/projects.csv")


def get_projects(
    technology: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Returns project records from the SharePoint project export."""

    projects = []

    with DATA_FILE.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            if technology:
                if row["technology"].lower() != technology.lower():
                    continue

            if status:
                if row["status"].lower() != status.lower():
                    continue

            row["percent_complete"] = int(
                row["percent_complete"]
            )

            projects.append(row)

    return projects
def get_at_risk_projects(
    technology: str | None = None,
) -> list[dict]:
    """Returns active projects with schedule or budget risk."""

    projects = get_projects(
        technology=technology,
        status="Active",
    )

    at_risk = []

    for project in projects:
        schedule_status = project["schedule_status"].lower()
        budget_status = project["budget_status"].lower()

        if (
            schedule_status in {"at risk", "behind"}
            or budget_status in {"at risk", "behind"}
        ):
            at_risk.append(project)

    return at_risk