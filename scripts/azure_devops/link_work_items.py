from pathlib import Path
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



def get_work_items():

    return client.get_work_items()



def find_item(items, title):

    for item in items:

        if item["fields"].get(
            "System.Title"
        ) == title:

            return item["id"]

    return None



def create_parent_link(
    child_id,
    parent_id
):

    client.link_work_items(
        child_id,
        parent_id
    )



projects = pd.read_csv(
    PROJECT_FILE
)


all_items = get_work_items()


print(
    f"Found {len(all_items)} work items"
)



for _, project in projects.iterrows():

    project_id = project["project_id"]

    project_name = project["project_name"]


    print(
        f"\nLinking {project_id}"
    )


    #
    # Epic
    #

    epic_title = (
        f"{project_id} - "
        f"{project_name}"
    )


    epic_id = find_item(
        all_items,
        epic_title
    )


    #
    # Feature
    #

    feature_title = (
        f"{project_id} Delivery "
        "Implementation"
    )


    feature_id = find_item(
        all_items,
        feature_title
    )



    #
    # Story
    #

    story_title = (
        f"{project_id} Complete "
        "delivery milestone"
    )


    story_id = find_item(
        all_items,
        story_title
    )



    if epic_id and feature_id:


        print(
            "Linking Feature -> Epic"
        )


        create_parent_link(
            feature_id,
            epic_id
        )



    if feature_id and story_id:


        print(
            "Linking Story -> Feature"
        )


        create_parent_link(
            story_id,
            feature_id
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


        task_title = (
            f"{project_id} - {task}"
        )


        task_id = find_item(
            all_items,
            task_title
        )


        if task_id and story_id:


            print(
                f"Linking Task {task}"
            )


            create_parent_link(
                task_id,
                story_id
            )



print(
    "\nHierarchy linking completed"
)