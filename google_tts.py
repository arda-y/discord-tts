import os
from google.cloud import texttospeech
from audio_source import BytesAudioSource
from config import RUNTIME_ENV


class GoogleTTS:

    def __init__(self):
        # adds credentials to environment
        if RUNTIME_ENV == "container":
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_API_KEY_FILE")
        elif RUNTIME_ENV == "local":
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-api-key.json"
        # creates a client from the credentials pulled from the environment
        self.ttsclient = texttospeech.TextToSpeechClient()

    def generate_audio(self, text: str, language_code, voice_code, speed):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed
        )

        response = self.ttsclient.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio = BytesAudioSource(response.audio_content)

        return audio
