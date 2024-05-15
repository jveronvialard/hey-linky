# Linky

<div align = "center">
<h1>
    <img src = "https://github.com/jveronvialard/hey-linky/blob/main/assets/images/linky.jpeg?raw=true" width = 200 height = 200>
<br>

</h1>

</div>

Do you love listening to podcast and videos from your favorite influencers, but find yourself drowning in the sea of content? Are you frustrated by missing out on crucial information, or struggling to distill key insights from lengthy episodes or videos?

Enter Linky, your personalized content companion. Linky revolutionizes information consumption by letting you interact with the content you like from your favorite social media channels, and can also fetch general information directly from the internet. Whether you're craving the latest releases or seeking key insights, Linky has you covered.

Just say "Hey Linky" to get started. You can also interact with Linky through a chat interface. Choose whatever works best for you at the moment you are seeking the information!

## System design

### Frontend
On iOS devices, Linky can be added as an Apple Shortcut and seamlessly integrates with Siri.

### Backend
You can run the Flask app inside a virtual instance or on your personal laptop. We use Groq for model inference, but our code can be modified to use other cloud-hosted genAI services or open-source / open-weights models running on either a virtual machine or your personal laptop (e.g. using ollama with llama3:8b).

### Cost
As of 5/13/2024:
- [Groq](https://wow.groq.com/): llama3-70b for $0.59 (resp. $0.79) per 1M input (resp. output) tokens;
- [Brave](https://brave.com/search/api/): a free account gives you 1 query per second and up to 2,000 queries per month;
- [AWS EC2](https://aws.amazon.com/ec2/instance-types/t2/): you can get a t2.small for $0.023/hour on-demand.

## How to use
Front-end tested with iOS only. You can also make post requests directly to the backend, e.g. using Python.

### Requirements
- YouTube. Using your Google account, log in to the Google Cloud Console. Search for "APIs & Services", then for "YouTube Data API v3". You will need to create an "API Keys" (add the API key to .env file) and a "OAuth 2.0 Client IDs" (download secrets as JSON and add to project root directory). In "OAuth consent screen", add yourself as "Test users". You can make 10,000 queries per day for free.
- Brave. Create a free account and add the API key to .env file.
- Groq. Create an account and add the API key to .env file.
- Weights & Biases (optional). Create a free account and add the API key to .env file.

The `.env` file should be at the project root directory and contain the following environment variables:
```
YOUTUBE_API_KEY=XXX
GROQ_API_KEY=XXX
BRAVE_API_KEY=XXX
```

Optionally, you can also add:
```
WANDB_PROJECT=XXX
WANDB_ENTITY=XXX
```

### Server
Create a conda environment, install the necessary packages, and start the app:
```
conda create -n linky-env python=3.9
conda activate linky-env
pip install -e .
python linky/app/app.py
```

If you are on a local laptop, the Google authentification flow happens in the browser. If you are on a virtual machine, you might be required to change the authentification flow, e.g. by creating a `google.oauth2.credentials.Credentials` object directly from your client_id, client_secret, and temporary token.

### Apple Shortcut
On your iPhone, go to Shortcuts, and create the following flow:
```
"Text" element with value "Hi, any questions?"
"Set variable" element with variable name "Prompt".
"Repeat" element. 10 times.
    "Get variable" element. Get "Prompt".
    "Ask for input" element. Text. "Prompt" variable.
    "Get contents of URL" element. "http://address:5000/". Set method to JSON and request body to JSON. Add "new field" of type "text" with key "prompt" and text "Provided Input" element.
    "Get text from" element.
    "Set variable" element with variable name "Prompt".
```
Then, rename the shortcut "Hey Linky". You're all set.

## Contributing
Feel free to open a PR. Use [pre-commit](https://pre-commit.com/) to automatically format your code. If you're using Windows, you might need to create a Python venv instead of using conda.
