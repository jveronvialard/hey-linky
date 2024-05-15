import copy
from groq import Groq
import json

from linky.core.brave import BraveData
from linky.core.youtube import YoutubeData


class Agent:
    def __init__(self, system_prompt, groq_api_key, brave_api_key, youtube_api_key, youtube_client_secret_file):       
        self.client = Groq(api_key=groq_api_key)
        self.YTD = YoutubeData(youtube_api_key=youtube_api_key, youtube_client_secret_file=youtube_client_secret_file)
        self.BD = BraveData(brave_api_key=brave_api_key)

        self.functions_mapping = {
            "get_videos_published_in_last_days": self.YTD.get_videos_published_in_last_days,
            "get_video_transcript": self.YTD.get_video_transcript,
            "get_all_video_descrition": self.YTD.get_all_video_descrition,
            "get_brave_search": self.BD.get_brave_search,
            "get_channel_description": self.YTD.get_channel_description,
        }
        self.tools = [
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

        self.system_prompt = system_prompt
        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
        ]  

    def reset(self):
        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
        ]

    def predict(self, messages, tool_choice="auto"):
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            tools=self.tools,
            tool_choice=tool_choice,
            max_tokens=4096,
            temperature=0,
        )
        return response.choices[0].message

    def run(self, prompt):
        self.messages += [
            {
                "role": "user",
                "content": prompt,
            }
        ]
            
        response = self.predict(self.messages, tool_choice="auto")
    
        if response.tool_calls:
    
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.functions_mapping[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
    
                if isinstance(function_response, dict):
                    function_response = json.dumps(function_response)
                if isinstance(function_response, list):
                    function_response = json.dumps(function_response)
    
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
        
                response = self.predict(self.messages, tool_choice="none")
    
        self.messages += [
            {
                "role": "assistant",
                "content": response.content,
            }
        ]
    
        return self.messages