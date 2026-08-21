from azdo_client import AzureDevOpsClient


client = AzureDevOpsClient()



bugs = [

    {

        "title":
        "PBI-004 API Integration Failure",

        "description":
        """
Project:
PBI-004

Issue:
API integration delay.

Impact:
Blocking delivery milestone.

Severity:
High

Risk:
Sprint commitment may slip.
""",

    },


    {

        "title":
        "D365-001 Data Validation Failure",

        "description":
        """
Project:
D365-001

Issue:
Source and target data mismatch.

Impact:
Testing blocked.

Severity:
Medium

Risk:
Delivery timeline impact.
"""

    }

]



for bug in bugs:


    print(
        f"Creating bug: {bug['title']}"
    )


    client.create_work_item(

        "Bug",

        bug["title"],

        bug["description"]

    )



print(
    "Risk bugs created successfully"
)