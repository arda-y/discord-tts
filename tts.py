import re
import sys
from datetime import datetime

import json
from google_tts import GoogleTTS
from nextcord import Message, FFmpegPCMAudio
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot
from nextcord.errors import ClientException

from audio_source import BytesAudioSource
from db_connector import Server, User, QuotaTracker


class TextToSpeech(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.google_tts = GoogleTTS()
        self.permission_to_restart = False

    @tasks.loop(seconds=5)
    async def check_voice_clients(self):
        try:
            if self.bot.voice_clients == []:
                return
            for client in self.bot.voice_clients:
                if (datetime.now() - client.last_activity).seconds > 180:
                    await client.disconnect()
        except AttributeError:  # no worries, keep working
            pass
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("starting tts cog")
        await self.check_voice_clients.start()

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        # parse user and channel id
        user: User = msg.author
        user_voice_channel = user.voice.channel if user.voice else None

        if msg.author.bot:
            return

        if user_voice_channel is None:
            return

        if msg.content.startswith("tts!") or msg.content.startswith("."):
            return  # ignore tts commands

        if not msg.channel.id == user_voice_channel.id:
            return

        def _find_url(string: str):
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            url = re.findall(regex, string)
            return [x[0] for x in url]

        def _replace_hyperlink(
            string: str,
        ):  # replace markdown hyperlinks with the display text
            regex = r"\[.*\]\((.*)\)"
            url = re.findall(regex, string)
            return [x[0] for x in url]

        def _remove_emojis(string: str):
            # <:Troll:1091878581099053077>
            # <a:Troll:1091878581099053077>
            # example of emoji
            regex = r"<a?:\w+:\d+>"
            return re.sub(regex, "", string)

        msg.content = _remove_emojis(msg.content)

        def _replace_discord_text(msg: Message):
            for mention in msg.mentions:
                msg.content = msg.content.replace(mention.mention, mention.display_name)
            for channels in msg.channel_mentions:
                msg.content = msg.content.replace(channels.mention, channels.name)
            for roles in msg.role_mentions:
                msg.content = msg.content.replace(roles.mention, roles.name)

        _replace_discord_text(msg)

        if _find_url(msg.content) or _replace_hyperlink(
            msg.content
        ):  # remove urls and read only text
            for url in _find_url(msg.content):
                msg.content = msg.content.replace(url, "")
            for url in _replace_hyperlink(msg.content):
                msg.content = msg.content.replace(url, url.split("]")[0][1:])

        if not 300 > len(msg.content.strip()) > 0:
            return

        user_db_data: User = await User.get_or_generate(user.id)
        server_db_data: Server = await Server.get_or_generate(msg.guild.id)

        audio_gen_lang_code = ""
        audio_gen_voice = ""
        audio_gen_speed = ""

        # 1- check server specific voice/lang
        # 2- check server default voice/lang
        # 3- check user default voice/lang
        # 4- check server specific speed
        # 5- check user default speed

        # 1- check server specific voice/lang
        try:
            server_specific_settings = json.loads(user_db_data.servers)[
                str(msg.guild.id)
            ]
            if server_specific_settings["lang"] == None:
                raise KeyError
            if server_specific_settings["voice"] == None:
                raise KeyError
            audio_gen_lang_code = server_specific_settings["lang"]
            audio_gen_voice = server_specific_settings["voice"]
        except KeyError:
            pass
        except Exception as e:
            print(e)

        # 2- check server default voice/lang
        if len(audio_gen_lang_code) == 0 or len(audio_gen_voice) == 0:
            try:
                if server_db_data.lang == None:
                    raise KeyError
                if server_db_data.voice == None:
                    raise KeyError
                audio_gen_lang_code = server_db_data.lang
                audio_gen_voice = server_db_data.voice
            except KeyError:
                pass
            except Exception as e:
                print(e)

        # 3- check user default voice/lang
        if len(audio_gen_lang_code) == 0 or len(audio_gen_voice) == 0:
            audio_gen_lang_code = user_db_data.default_lang
            audio_gen_voice = user_db_data.default_voice

        # 4- check server specific speed
        try:
            server_specific_settings = json.loads(user_db_data.servers)[
                str(msg.guild.id)
            ]
            if server_specific_settings["speed"] == None:
                raise KeyError
        except KeyError:
            pass
        except Exception as e:
            print(e)

        # 5- check user default speed
        if len(audio_gen_speed) == 0:
            audio_gen_speed = user_db_data.default_speed

        # debug point
        print(
            f"User: {user.id}"
            f"\nServer: {msg.guild.id}"
            f"\nText: {msg.content}"  # lenght of msg.content is gonna be added to character limit
            f"\nLanguage: {audio_gen_lang_code}"
            f"\nVoice: {audio_gen_voice}"
            f"\nSpeed: {audio_gen_speed}"
        )

        audio: BytesAudioSource = self.google_tts.generate_audio(
            text=msg.content,
            language_code=audio_gen_lang_code,
            voice_code=audio_gen_voice,
            speed=float(audio_gen_speed),
        )  # generate audio from text

        _ = await QuotaTracker.add_to_quota(
            len(msg.content)
        )  # add to quota if voice is generated

        await User.add_characters_used(user.id, len(msg.content))
        # add to user's character count

        if self.bot.voice_clients == []:  # no voice clients
            client = await user_voice_channel.connect()
            client.play(FFmpegPCMAudio(source=audio.get_path()))
            client.last_activity = datetime.now()

        else:
            for client in self.bot.voice_clients:
                # every single connection is for one guild only
                # check if in guild's voice channel
                # if not then connect, otherwise check for channel match
                if (
                    client.guild.id == msg.guild.id
                ):  # bot is connected to guild's voice channel
                    if client.channel.id == user_voice_channel.id:
                        # bot is connected to the same channel as user
                        try:
                            client.play(FFmpegPCMAudio(source=audio.get_path()))
                            client.last_activity = datetime.now()
                        except ClientException as e:
                            if "Not connected to voice." in str(e):
                                await msg.reply(
                                    "Encountered internal error that's not explicitly handled, please report this to the developer. Restarting the bot, please wait for a few seconds."
                                    + f"Error log: {str(e)[:1700]}"  # discord character limit is 2000, 1700 is a safe bet
                                )
                                sys.exit(0)
                            elif "Already playing audio." in str(e):
                                # no queue system yet, and probably not in the future, safe to ignore
                                pass
                            else:
                                await msg.reply(
                                    "Encountered internal error that's not explicitly handled, please report this to the developer. Restarting the bot, please wait for a few seconds."
                                    + f"Error log: {str(e)[:1700]}"  # discord character limit is 2000, 1700 is a safe bet
                                )
                                sys.exit(0)
                    break


def setup(bot: Bot):
    bot.add_cog(TextToSpeech(bot))
