from azdo_client import AzureDevOpsClient


client = AzureDevOpsClient()


links = {

    "PBI-004 API Integration Failure":
        "PBI-004 Complete delivery milestone",


    "D365-001 Data Validation Failure":
        "D365-001 Complete delivery milestone"

}



items = client.get_work_items()



def find_id(title):

    for item in items:

        if item["fields"].get(
            "System.Title"
        ) == title:

            return item["id"]

    return None



for bug, story in links.items():


    bug_id = find_id(
        bug
    )


    story_id = find_id(
        story
    )


    if bug_id and story_id:


        print(
            f"Linking {bug} -> {story}"
        )


        client.link_work_items(

            bug_id,

            story_id

        )



print(
    "Risk linking completed"
)