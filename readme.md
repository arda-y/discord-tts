# ttsbot - as simple as it gets

A simple discord bot that uses the google text-to-speech API to read messages in voice channels.

## Installation

<div>
<img src="https://cdn.discordapp.com/attachments/1170481425716355075/1266746276796698676/68747470733a2f2f6a6f68616e2e647269657373656e2e73652f696d616765732f6a6f68616e5f647269657373656e5f73652f57696e646f77734c6976655772697465722f50657273697374616e6365696e57463462657461325f453441442f776f726b732d6f6e2d6d.png?ex=66a644e7&is=66a4f367&hm=d951ad7f1eb4973fab67154145df4c3a8688d09bdef555775ab3d9db43381446&" align: center; />
</div>

(works on my machine, so you get instructions for my machine, go figure)

1- Clone the repository

```bash
git clone https://github.com/kirellkekw/discord-tts.git
cd discord-tts # assuming you cloned it into the current directory
```

2- Install the requirements

- Have python 3.11+ and FFmpeg installed before going any further

```bash
pip install -r requirements.txt
```

3- Create a Discord bot and get the token

- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application
- Go to the "Bot" tab and create a new bot
- Copy the token
- Enable all intents in the "Bot" tab(it's probably not all of them, not going to verify that)
- in Bot scope, enable "Read Messages", "Connect" and "Speak" permissions
- Generate an OAuth2 URL and invite the bot to your server
- Paste the token into the `discord-token.txt` file in the root directory of the project

4- Get a Google Cloud API key

- Go to the [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project
- Enable the "Text-to-Speech API", probably in [this link](https://console.cloud.google.com/apis/api/texttospeech.googleapis.com)(not going to verify that either)
- Create a service account
- Download the JSON key file
- Rename the JSON key file to `google-api-key.json`
- Move the JSON key file to the root directory of the project

5- Run the bot

- Before running the bot, change the values in `config.py`, such as the prefix and owner id.

```bash
python main.py
```

bon appétit, run `!tts help` in a text channel to get a list of commands

## License

Glorbo Florbo personally emailed me this project while I was drinking beypazarı mineral water on an unusually
hot wednesday at 2.49pm. So, feel free to use it however you like, but don't tell Glorbo Florbo
about it.

- i'm not responsible for any damage caused by this bot, including but not limited to:
  - everyone in the voice channel leaving
  - frustration caused during the installation process
  - irritated ear drums caused by irresponsible use of the bot
  - possible anger issues caused by bot not working as intended
  - Glorbo Florbo visiting your house and demanding royalties for using his code

### dev notes

- will add docker support at some point
- keyword being "at some point", don't hold your breath
- code is highly borked, don't look at it
- bot it theoretically harmless except for the fact that it can read your messages out very slowly, which is a form of torture
