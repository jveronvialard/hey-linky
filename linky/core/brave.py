import json

import requests


class BraveData:
    def __init__(self, brave_api_key):
        self.brave_api_key = brave_api_key

    def get_brave_search(self, query):
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key,
        }

        params = {
            "q": query,
            "summary": "1",
        }

        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params=params,
            headers=headers,
        )
        content = json.loads(response.content)
        return content["infobox"]["results"][0]["long_desc"]
