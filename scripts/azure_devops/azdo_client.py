import os
import base64
import requests

from urllib.parse import quote
from dotenv import load_dotenv


load_dotenv()


class AzureDevOpsClient:

    def __init__(self):

        self.organization = os.getenv(
            "AZDO_ORG"
        )

        self.project = os.getenv(
            "AZDO_PROJECT"
        )

        self.pat = os.getenv(
            "AZDO_PAT"
        )


        if not all(
            [
                self.organization,
                self.project,
                self.pat
            ]
        ):

            raise ValueError(
                "Missing AZDO_ORG, AZDO_PROJECT or AZDO_PAT"
            )


        token = base64.b64encode(
            f":{self.pat}".encode()
        ).decode()


        self.headers = {

            "Authorization":
                f"Basic {token}",

            "Content-Type":
                "application/json-patch+json"

        }


        self.base_url = (

            f"https://dev.azure.com/"
            f"{self.organization}/"
            f"{self.project}/"
            f"_apis"

        )



    # -------------------------------------------------
    # CREATE WORK ITEM
    # -------------------------------------------------

    def create_work_item(
            self,
            work_item_type,
            title,
            description="",
            story_points=None
    ):


        encoded_type = quote(
            work_item_type
        )


        url = (

            f"{self.base_url}/wit/"
            f"workitems/"
            f"${encoded_type}"
            f"?api-version=7.0"

        )


        body = [

            {

                "op": "add",

                "path":
                "/fields/System.Title",

                "value":
                title

            },

            {

                "op": "add",

                "path":
                "/fields/System.Description",

                "value":
                description

            }

        ]


        if story_points is not None:


            body.append(

                {

                    "op":
                    "add",

                    "path":
                    "/fields/"
                    "Microsoft.VSTS.Scheduling.StoryPoints",

                    "value":
                    story_points

                }

            )


        response = requests.post(

            url,

            headers=self.headers,

            json=body

        )


        if not response.ok:

            print(
                "\nAzure DevOps Error:"
            )

            print(
                response.text
            )


        response.raise_for_status()


        return response.json()



    # -------------------------------------------------
    # GET ALL WORK ITEMS
    # -------------------------------------------------

    def get_work_items(self):


        wiql_url = (

            f"{self.base_url}/wit/"
            f"wiql"
            f"?api-version=7.0"

        )


        query = {

            "query":

            """
            SELECT
            [System.Id]
            FROM WorkItems
            ORDER BY [System.Id]
            """

        }


        response = requests.post(

            wiql_url,

            headers={
                **self.headers,

                "Content-Type":
                "application/json"

            },

            json=query

        )


        if not response.ok:

            print(
                response.text
            )


        response.raise_for_status()


        ids = [

            item["id"]

            for item

            in response.json()
            .get(
                "workItems",
                []
            )

        ]


        if not ids:

            return []



        ids_string = ",".join(

            map(
                str,
                ids
            )

        )



        details_url = (

            f"{self.base_url}/wit/"
            f"workitems"
            f"?ids={ids_string}"
            f"&api-version=7.0"

        )


        details_response = requests.get(

            details_url,

            headers=self.headers

        )


        details_response.raise_for_status()


        return details_response.json()["value"]

    def update_work_item_iteration(
            self,
            work_item_id,
            iteration_path
    ):


        url = (

            f"{self.base_url}/wit/"
            f"workitems/{work_item_id}"
            f"?api-version=7.0"

        )


        body = [

            {

                "op":
                "add",

                "path":
                "/fields/System.IterationPath",

                "value":
                iteration_path

            }

        ]


        response = requests.patch(

            url,

            headers=self.headers,

            json=body

        )


        if not response.ok:

            print(response.text)


        response.raise_for_status()



    # -------------------------------------------------
    # CREATE PARENT CHILD LINK
    # -------------------------------------------------

    def link_work_items(

            self,

            child_id,

            parent_id

    ):


        url = (

            f"{self.base_url}/wit/"
            f"workitems/{child_id}"
            f"?api-version=7.0"

        )



        parent_url = (

            f"https://dev.azure.com/"
            f"{self.organization}/"
            f"{self.project}/"
            f"_apis/wit/workItems/"
            f"{parent_id}"

        )



        body = [

            {

                "op":
                "add",

                "path":
                "/relations/-",

                "value":

                {

                    "rel":
                    "System.LinkTypes.Hierarchy-Reverse",

                    "url":
                    parent_url

                }

            }

        ]



        response = requests.patch(

            url,

            headers=self.headers,

            json=body

        )



        if not response.ok:

            print(
                "\nLinking Error:"
            )

            print(
                response.text
            )


        response.raise_for_status()


        return response.json()

    def update_work_item_state(
            self,
            work_item_id,
            state
    ):


        url = (

            f"{self.base_url}/wit/"
            f"workitems/{work_item_id}"
            f"?api-version=7.0"

        )


        body = [

            {

                "op":
                "add",

                "path":
                "/fields/System.State",

                "value":
                state

            }

        ]


        response = requests.patch(

            url,

            headers=self.headers,

            json=body

        )


        if not response.ok:

            print(
                response.text
            )


        response.raise_for_status()