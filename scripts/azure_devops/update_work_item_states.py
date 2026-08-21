from azdo_client import AzureDevOpsClient


client = AzureDevOpsClient()


state_mapping = {


    "PBI-001 Complete delivery milestone":
        "Closed",


    "PBI-002 Complete delivery milestone":
        "Closed",


    "PBI-003 Complete delivery milestone":
        "Resolved",


    "PBI-004 Complete delivery milestone":
        "Active",


    "AZ-001 Complete delivery milestone":
        "Active",


    "D365-001 Complete delivery milestone":
        "New",


    "PBI-005 Complete delivery milestone":
        "New"

}



items = client.get_work_items()



for item in items:


    title = item["fields"].get(
        "System.Title"
    )


    if title in state_mapping:


        state = state_mapping[title]


        print(
            f"{title} -> {state}"
        )


        client.update_work_item_state(

            item["id"],

            state

        )



print(
    "State update completed"
)