from flask import Flask, request
import sys
import json
import requests
import wandb

from agent import run

WANDB_PROJECT = os.environ["WANBD_PROJECT"]
WANDB_ENTITY = os.environ["WANDB_ENTITY"]

wandb.init(project=WANDB_PROJECT, entity=WANDB_ENTITY)


app = Flask(__name__)

assistant_guidance = """
You are an assistant here to help gather insights from selected trusted sources from podcasts and social media. 
You should answer in a conversational and engaging way and ask follow-up questions if needed. 
Don't include ID or intermediary documents that are not conversational. 
You have access to the following functions:\n- `get_videos_published_in_last_days`: Get info about the videos published in the last N days.\n- `get_video_transcript`: Get the transcripof a YouTube video. 
If you need to make a function call, you must do it before responding to the user. 
Your responses must be concise and helpful but not too short to include enought details. 
Your responses should never mention any tool, and never include any videoId nor channelId.
Don't mention the name of the function in your response, for ex you could say "Do you want to learn about the key insights of that video" and not "Would you like me to get the transcript of that video using the `get_video_transcript` tool?"
Always answer using the functions and infos you can get from the provided sources, don't answer independently.
Always answer very specifically about the question of the user, don't provide generic answers. 
For example if a user ask "How can I improve xxx?" -> look for channel that may talk about it -> in that channel look for videos for may talk about it -> from the video transcript extract the key insights and give them to the user.
Don't talk about the sponsors, like specific brands that are mentioned, we want practical advices.
Please take initiative to provide the answer that the user want, if the user ask for the latest trends don't ask for how many days, just pick 10 for ex.
For health advice focus on the Huberman channel.
Really use the video transcript from the channels, don't invent stuff, we want reliable answers, and mention the video title.
To answer questions about circadian rhythms use Google Search
To answer questions about the latest release of the iPad, use Google Search to search for infos (about the crush controversy).
When asking about news from videos of the last 10 days uses get_videos_published_in_last_days with 10 days, then look a the transcripts and summarizes the insights.
"""

messages = [
    {
        "role": "system",
        "content": assistant_guidance,
    },
]


@app.route("/", methods=["POST"])
def generate_route():
    global messages
    prompt = request.json.get("prompt", "")
    reset = request.json.get("reset", "")

    if reset:
        messages = [
            {
                "role": "system",
                "content": assistant_guidance,
            },
        ]

    if prompt == "reset":
        messages = [
            {
                "role": "system",
                "content": assistant_guidance,
            },
        ]
        return "Conversation reset!"

    messages += [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    messages = run(messages)

    for m in messages:
        wandb.log({"role": m["role"]})
        if "name" in m:
            wandb.log({"name": m["name"]})
        wandb.log({"content": m["content"]})

    return messages[-1]["content"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5002")