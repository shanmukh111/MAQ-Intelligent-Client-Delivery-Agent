from pathlib import Path
import random

import pandas as pd

from azdo_client import AzureDevOpsClient



BASE_DIR = Path(__file__).resolve().parents[2]


PROJECT_FILE = (
    BASE_DIR
    /
    "data"
    /
    "sharepoint"
    /
    "projects.csv"
)


client = AzureDevOpsClient()


projects = pd.read_csv(
    PROJECT_FILE
)


print(
    f"Loaded {len(projects)} projects"
)



for _, project in projects.iterrows():


    project_id = project["project_id"]

    project_name = project["project_name"]

    status = str(
        project.get(
            "status",
            ""
        )
    )

    schedule = str(
        project.get(
            "schedule_status",
            ""
        )
    )

    risk = str(
        project.get(
            "risk_summary",
            ""
        )
    )

    technology = str(
        project.get(
            "technology",
            ""
        )
    )

    percent_complete = project.get(
        "percent_complete",
        0
    )


    print(
        f"\nCreating data for {project_id}"
    )


    #
    # Epic
    #

    client.create_work_item(

        "Epic",

        f"{project_id} - {project_name}",

        f"""
Project ID:
{project_id}

Project:
{project_name}

Technology:
{technology}

Status:
{status}

Completion:
{percent_complete}%

Schedule:
{schedule}

Risk:
{risk}
"""

    )


    #
    # Feature
    #

    client.create_work_item(

        "Feature",

        f"{project_id} Delivery Implementation",

        f"""
Delivery implementation activities
for {project_name}
"""

    )


    #
    # User Story
    #

    client.create_work_item(

        "User Story",

        f"{project_id} Complete delivery milestone",

        f"""
Complete milestone activities
for {project_name}
""",

        story_points=random.randint(
            5,
            20
        )

    )


    #
    # Tasks
    #

    tasks = [

        "Development implementation",

        "Data validation",

        "Testing and verification"

    ]


    for task in tasks:


        client.create_work_item(

            "Task",

            f"{project_id} - {task}",

            task

        )


    #
    # Bugs for risky projects
    #

    risky = (

        "risk" in status.lower()

        or

        "behind" in schedule.lower()

        or

        "high" in risk.lower()

    )


    if risky:


        client.create_work_item(

            "Bug",

            f"{project_id} Delivery Risk Issue",

            f"""
Generated delivery risk issue.

Risk:
{risk}

Schedule:
{schedule}
"""

        )



print(
    "\nAzure DevOps seeding completed successfully."
)