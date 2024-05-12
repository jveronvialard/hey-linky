import os
import sys

import copy
from groq import Groq
import json
import os
import sys
import requests

from core.data_processing import YoutubeData


GROQ_API_KEY = os.environ["GROQ_API_KEY"]
BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]


def get_brave_search(query):
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    params = {
        "q": query,
        "summary": "1",
    }

    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search", params=params, headers=headers
    )
    content = json.loads(response.content)
    return content["infobox"]["results"][0]["long_desc"]


def predict(client, messages, tools, tool_choice="auto"):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        max_tokens=4096,
        temperature=0,
    )
    return response.choices[0].message


client = Groq(api_key=GROQ_API_KEY)

YTD = YoutubeData()


FUNCTIONS_MAPPING = {
    "get_videos_published_in_last_days": YTD.get_videos_published_in_last_days,
    "get_video_transcript": YTD.get_video_transcript,
    "get_all_video_descrition": YTD.get_all_video_descrition,
    "get_brave_search": get_brave_search,
    "get_channel_description": YTD.get_channel_description,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_videos_published_in_last_days",
            "description": "Get metadata about the videos recently published in the YouTube channels you subscribed to",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days in the past",
                    }
                },
                "required": ["days"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_video_transcript",
            "description": "Get the full transcript of a YouTube video. You must use it for summarizing a video or answering questions about it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "videoId": {
                        "type": "string",
                        "description": "ID of a video",
                    }
                },
                "required": ["videoId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_brave_search",
            "description": "Search for external information using Brave browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Your query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_description",
            "description": "Get the full the description of all channels that the user is subscribed to. Helpful for answering questions about a specific topics when you need to figure out which channel will have relevant content about it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "videoId": {
                        "type": "string",
                        "description": "ID of a video",
                    }
                },
                "required": ["videoId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_video_descrition",
            "description": "Get the description of all videos in a given channel. Helful once you know that a channel with talk about a given topic and want to know which specific videos are relevant. The output is on a dict format with video_id as key and description as value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "videoId": {
                        "type": "string",
                        "description": "ID of a video",
                    }
                },
                "required": ["videoId"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a function calling LLM. You have access to the following functions:

- get_videos_published_in_last_days: Get info about the videos published in the last N days.
- get_video_transcript: Get the transcript of a YouTube video.
- get_brave_search: Search for external information using Brave browser.
- get_channel_description: Get the full the description of all channels that the user is subscribed to. Helpful for answering questions about a specific topics when you need to figure out which channel will have relevant content about it.
- get_all_video_descrition: Get the description of all videos in a given channel. Helful once you know that a channel with talk about a given topic and want to know which specific videos are relevant. The output is on a dict format with video_id as key and description as value.

"""


def run(messages):
    messages = copy.deepcopy(messages)

    response = predict(client, messages, TOOLS, tool_choice="auto")

    if response.tool_calls:

        for tool_call in response.tool_calls:
            function_name = tool_call.function.name
            function_to_call = FUNCTIONS_MAPPING[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            if isinstance(function_response, dict):
                function_response = json.dumps(function_response)
            if isinstance(function_response, list):
                function_response = json.dumps(function_response)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        response = predict(client, messages, TOOLS, tool_choice="none")

    messages += [
        {
            "role": "assistant",
            "content": response.content,
        }
    ]

    return messages