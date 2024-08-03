# ttsbot - as simple as it gets

A simple discord bot that uses the google text-to-speech API to read messages in voice channels.

## Installation

<div>
<img src="https://blog.codinghorror.com/content/images/uploads/2007/03/6a0120a85dcdae970b0128776ff992970c-pi.png" align: center; />
</div>

(works on my machine, so you get instructions for my machine, go figure)

1- Clone the repository

```bash
git clone https://github.com/kirellkekw/discord-tts.git
cd discord-tts # assuming you cloned it into the current directory
```

2- Install the requirements

- docker
- ffmpeg

3- Create a Discord bot and get the token

- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application
- Go to the "Bot" tab and create a new bot
- Copy the token
- Enable all intents in the "Bot" tab(it's probably not all of them, not going to verify that)
- in Bot scope, enable "Read Messages", "Connect" and "Speak" permissions
- Generate an OAuth2 URL and invite the bot to your server
- Create a new file called `discord-token.txt` in the root directory of the project and paste the token into it

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

- Run the bot

```bash
docker compose up -d
```

bon appétit, run `!tts help` in a text channel to get a list of commands

## License

Glorbo Florbo personally emailed me this project while I was drinking Beypazarı(TM) mineral water on an unusually
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
