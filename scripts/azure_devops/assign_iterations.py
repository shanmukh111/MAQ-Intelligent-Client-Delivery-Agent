from pathlib import Path
import pandas as pd

from azdo_client import AzureDevOpsClient


client = AzureDevOpsClient()


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



def get_iteration_name(project_id):

    mapping = {

        "PBI-001": "Iteration 1",
        "PBI-002": "Iteration 1",

        "PBI-003": "Iteration 2",

        "PBI-004": "Iteration 3",
        "AZ-001": "Iteration 3",
        "D365-001": "Iteration 3",

        "PBI-005": "Iteration 3"

    }

    return mapping.get(
        project_id,
        "Iteration 1"
    )



def update_iteration(
        work_item_id,
        iteration_path
):


    client.update_work_item_iteration(
        work_item_id,
        iteration_path
    )



items = client.get_work_items()


projects = pd.read_csv(
    PROJECT_FILE
)



for _, project in projects.iterrows():

    project_id = project["project_id"]


    iteration = get_iteration_name(
        project_id
    )


    print(
        f"{project_id} -> {iteration}"
    )


    story_title = (
        f"{project_id} Complete "
        "delivery milestone"
    )


    for item in items:


        title = item["fields"].get(
            "System.Title"
        )


        if title == story_title:


            update_iteration(

                item["id"],

                f"MAQ-Intelligent-Delivery-Agent\\{iteration}"

            )



print(
    "Iteration assignment completed"
)