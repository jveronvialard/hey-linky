import argparse
from dotenv import load_dotenv
from flask import Flask, request
import os

from linky.core.agent import Agent
from linky.core.logger import Logger
from linky.core.constants import SYSTEM_PROMPT


load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
WANDB_PROJECT = os.environ.get("WANBD_PROJECT", None)
WANDB_ENTITY = os.environ.get("WANDB_ENTITY", None)


app = Flask(__name__)


@app.route("/", methods=["POST"])
def generate_route():
    global agent
    prompt = request.json.get("prompt", "")
    logger.log("prompt", prompt)

    if prompt in ["", "reset"]:
        agent.reset()
        return "Conversation reset!"

    else:
        messages = agent.run(prompt=prompt)
    
        for m in messages:
            logger.log("role", m["role"])
            if "name" in m:
                logger.log("name", m["name"])
            logger.log("content", m["content"])
    
        return messages[-1]["content"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Linky app')
    parser.add_argument("--youtube_client_secret_file", type=str, default="client_secret.json")
    parser.add_argument("--port", type=str, default="5000")
    args = parser.parse_args()

    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        groq_api_key=GROQ_API_KEY,
        brave_api_key=BRAVE_API_KEY,
        youtube_api_key=YOUTUBE_API_KEY,
        youtube_client_secret_file=args.youtube_client_secret_file
    )
    
    logger = Logger(
        wandb_project=WANDB_PROJECT,
        wandb_entity=WANDB_ENTITY
    )

    app.run(host="0.0.0.0", port=args.port)